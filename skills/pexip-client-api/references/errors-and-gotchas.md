# Errors and Gotchas — Reference

This page collects every error-shape, status-code, and subtle-gotcha worth
internalising before you ship a Client API integration.

---

## The response envelope, reviewed

```jsonc
{ "status": "success" | "failure", "result": <payload> }
```

| `status` | Meaning |
|---|---|
| `"success"` | Pexip processed the command. `result` is the payload. |
| `"failure"` | Pexip refused the command. `result` is a short reason string. |
| `"failed"` *(past tense, only seen on `/status`)* | Same as `"failure"`, with inconsistent casing. Handle both. |

Always check **both** the HTTP status and the JSON `status` field. They're
not redundant — sometimes you'll see 200 with `"status": "success"` and a
nested `idp` or `redirect_url` field that means "you must do another
step". See `references/token-lifecycle.md` for the `request_token`
state machine.

---

## Status codes you'll see

| HTTP | Typical meaning |
|---|---|
| **200** | Success, or "another step needed" (read the body). |
| **400** | Bad request — usually a missing/invalid field. Specifics not documented; logs are the way to debug. |
| **401** | Token invalid or expired. **Not documented but commonly observed.** Re-`request_token`. |
| **403** | Auth-stage prompt: PIN required, IDP-list required, virtual-reception, display-name required. Inspect `result`. |
| **404** | Conference alias doesn't exist on this node, or participant UUID not in this conference. |
| **502 / 503** | Node in maintenance or upstream issue. For `/status`, 503 is the explicit "in maintenance" signal. |

If you see anything else (5xx, network errors), treat it as transient and
retry with backoff — Pexip doesn't publish rate-limit details and there's
no `Retry-After` header in normal operation.

---

## Auth-time failure shapes

These are the `request_token` "you must do another step" responses, all
returned (usually) with 4xx HTTP codes but `"status": "success"`/`"failure"`
varying by version. Pattern-match on `result`, not on HTTP code.

| `result` contains | Meaning | Next step |
|---|---|---|
| `{ "pin": "required", "guest_pin": "required" \| "none" }` | PIN required (specifies which roles). | Resubmit with `pin` field. Use `"none"` if only host has a PIN and you're a guest. |
| `{ "idp": [ … ] }` | SSO required. Pick from list. | Resubmit with `chosen_idp`. |
| `{ "redirect_url": "...", "redirect_idp": {…} }` | IDP redirect URL. | User authenticates at IDP; capture returning SAML/JWT; resubmit with `sso_token`. |
| `{ "conference_extension": "standard" \| "mssip" }` | Alias is a Virtual Reception dispatcher. | Resubmit with `conference_extension` = target alias. |
| `{ "display_name": "required" }` | Post-SSO, no name available. | Resubmit with a real `display_name` string. |

A real "you can't join this conference" failure will look like
`{"status":"failure","result":"<reason string>"}` with no structured
fields — just a human-readable string.

---

## Token-related gotchas

1. **Token expiry is not signalled in advance.** Track the `expires` value
   from `request_token` and refresh on a separate timer (recommended:
   every `expires/2` seconds).

2. **`refresh_token` returns a new token.** The old one is **immediately
   invalid** once you've seen the response. Update your shared store
   before issuing any new requests.

3. **You can't refresh after expiry.** `refresh_token` itself requires a
   live token. Once expired, only `request_token` recovers — and you may
   get a fresh `participant_uuid` (the participant is gone).

4. **One token per participant.** Two requests with the same token are
   two requests from the same participant. There's no concept of
   parallel sessions from one token.

5. **Concurrent refresh requests race.** If two coroutines/threads both
   call `refresh_token` at once, both get new tokens — one of which the
   other immediately invalidates. Always serialise refresh.

6. **The token in the `token:` header is case-sensitive on the value.**
   Don't trim, don't URL-decode (Pexip's tokens don't contain `%`-encoded
   characters but they do contain `+` and `=` — pass them through
   verbatim).

7. **`Authorization: Bearer …` is *not* accepted.** The header is
   literally named `token`. (And the value is *not* prefixed with
   `Bearer`.)

---

## SSE gotchas

1. **No `Last-Event-ID` semantics.** Reconnects always start fresh,
   bracketed by `participant_sync_*`. Don't try to dedupe events across
   reconnects — there is no event ID.

2. **`participant_update` is *not* a diff.** It's the full participant
   object on every change. If you want to know "what changed", diff
   against your stored copy.

3. **`participant_create` fires for snapshot rows too.** Inside the sync
   bracket, treat them as upserts, not "someone just joined" events.
   Otherwise you'll spam your "Alice joined" toast on every reconnect.

4. **Empty data lines.** Some events (`participant_sync_begin`,
   `participant_sync_end`, `presentation_stop`, `peer_disconnect`) carry
   no payload. Your SSE parser must handle "event line with empty data
   line" cleanly.

5. **Browsers auto-reconnect EventSource.** Most clients are fine with
   that. If you need to surface the reconnect (to UI, to log), you'll
   need to manage SSE manually with `fetch` + `ReadableStream`.

6. **Token in query string is logged.** Pexip Conferencing Node access
   logs may record the full URL, including `?token=…`. In production,
   redact or rotate logs. The `token` header form avoids this for
   non-SSE endpoints; for SSE there's no way around it from a browser
   (custom headers aren't possible on `EventSource`).

---

## Conference-and-alias gotchas

1. **Aliases may contain `@`, `+`, `.`, `_`.** URL-encode the alias in
   the path. Some HTTP clients leave `@` unencoded by default — check.

2. **Case sensitivity is configuration-dependent.** Most Pexip
   deployments are case-insensitive on aliases; some aren't. Don't rely
   on it; lowercase the alias when storing/comparing.

3. **A 404 on `request_token` means the alias didn't match anything on
   this Conferencing Node.** Could be configuration, could be a typo, or
   could be that this particular node doesn't host this alias's
   location. Verify the alias and try a different node.

4. **Conferencing Nodes don't all see all conferences uniformly.**
   Geographic deployments split media; a conference can be live on one
   node and unstarted on another. Always go through DNS / a load
   balancer / your locator, not a hardcoded node IP, in production.

5. **Conference identity is *the alias*, not a UUID.** Two participants
   on different nodes can both be "in" the same conference; they share
   the alias, but the per-node `conference_status` is independent.

---

## Multi-node observations

| Scenario | What happens |
|---|---|
| A conference is hosted on N Conferencing Nodes | Each node's SSE stream sees **all** participants (Pexip syncs roster across nodes). |
| A participant moves between nodes mid-call | Doesn't happen — the participant's call stays on the node it was set up on. |
| The node you're connected to goes offline | Your token, your SSE stream, your call — all gone. Reconnect to a different node with a new `request_token`. |
| You want a "global" admin view | Use the **Management API**, not the Client API. The Client API is participant-scoped. |

---

## Version skew

> "This API specification is regularly evolving between versions of the
> Pexip Infinity platform. While we will attempt to maintain backward
> compatibility, there may be significant changes between versions."

Observed practice:

- **New fields in responses** appear regularly. Read what you need; ignore
  the rest.
- **New event names** appear regularly. Always have a default branch in
  your dispatcher.
- **Endpoints rarely disappear**, but field semantics can change in major
  releases (e.g. v37 → v41 adds AC layouts, ducking, pinning, AI). If your
  code reads new fields, also handle them being absent on older nodes.
- **No version-skew error response** — if you POST to a v41 endpoint
  against a v37 node, you'll most likely get a 404.

If your integration must support a range of Infinity versions, treat
`version.version_id` from `request_token` as the source of truth and feature-detect
in your control flow.

---

## Long list of subtle gotchas

1. `Authorization: Bearer …` doesn't work; the header is literally `token`.

2. `request_token` 4xx + a `result` object is not a real failure — it's a
   state-machine prompt. Pattern-match on `result` keys.

3. `expires` is a string. Parse to int.

4. `pin: "none"` is a real value, used when only one role has a PIN.

5. `display_name: false` (boolean) means "ask the IDP" — different from
   omitting the field.

6. `role` is `"HOST"`/`"GUEST"` in token responses but `"chair"`/`"guest"`
   in participant objects.

7. `is_muted` is a `"YES"`/`"NO"` string; `is_video_muted` is a boolean.
   Several other YES/NO vs bool inconsistencies — normalise at parse time.

8. `participant_update` is full state, not delta. Diff yourself if needed.

9. `participant_sync_begin` fires on every reconnect. Don't treat as
   "session started".

10. Empty SDP answer from `/calls` in direct-media mode = "wait for
    `new_offer`", not an error.

11. `/ack` is the "start RTP" trigger, not an HTTP acknowledgement.

12. `message` is *chat*; `set_message_text` is a *banner*. Different
    endpoints, different UX.

13. `transform_layout` partial bodies are fine — only include the fields
    you want to change.

14. `dial` and `breakouts` create resources and aren't idempotent. Avoid
    blind retries.

15. `release_token` after a network blip is best-effort — if it doesn't
    reach Pexip, the participant times out naturally. Don't block your
    shutdown on it.

16. The maintenance `/status` endpoint uses `"failed"` not `"failure"`.

17. `current_service_type: "waiting_room"` is *not* an error — you got a
    token, but you can't do anything until you're admitted.

18. Conference aliases need URL-encoding for `@`/`+`. Some HTTP libraries
    don't encode `@` automatically.

19. `last_spoken_time` is float seconds since epoch, not ms.

20. `live_captions` events only arrive after a host-issued
    `show_live_captions` on that participant.

21. `presentation_frame` is a *signal* (empty payload). The JPEG lives at
    `/presentation.jpeg`; fetch on signal.

22. FECC and DTMF endpoints exist at both participant-level and call-level
    — participant-level is usually simpler.

23. `host_custom_properties` is only sent to hosts. Guest code can't read
    it — don't depend on it being present.

24. `participants` in the `layout` event can be empty (API-only
    participants). Don't treat as "no one in the conference".

25. The Pexip Client API is not the Pexip Management API. Different host,
    different paths, different auth model. Don't mix them up.
