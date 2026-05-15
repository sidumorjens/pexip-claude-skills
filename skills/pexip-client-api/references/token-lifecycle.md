# Token Lifecycle — Reference

The Client API is gated by a per-participant token. Three endpoints govern its
lifecycle:

| Endpoint | Purpose |
|---|---|
| `POST /request_token` | Obtain a new token (and discover what's required to join — PIN, IDP, conference extension). |
| `POST /refresh_token` | Extend an existing token before it expires. |
| `POST /release_token` | Surrender the token (graceful disconnect). |

All three live under `/api/client/v2/conferences/<alias>/`.

---

## 1. `POST /request_token`

This endpoint does double duty: it's both the authentication entry point and
the **discovery** endpoint. It can succeed, fail, or come back asking you to
do another step (provide a PIN, pick an IDP, complete an SSO redirect, target
a real conference, etc.). Treat every response as a step in a state machine.

### Request body

```jsonc
{
  "display_name": "Alice",            // required, OR set to `false` to derive from IDP
  "call_tag": "ops-bot-7",            // optional, your own correlation id
  "direct_media": true,               // optional, true if you can do direct-media WebRTC
  "pin": "1234",                      // optional — required if conference is PIN-protected
  "chosen_idp": "<idp-uuid>",         // optional — IDP UUID after first SSO step
  "sso_token": "<SAML or JWT>",       // optional — after IDP redirect
  "conference_extension": "meet.alice" // optional — only for Virtual Reception
}
```

Field notes:

- **`display_name`** — required field. Pass the user's name. If you want Pexip
  to derive the name from the IDP (post-SSO), pass the literal boolean `false`.
- **`call_tag`** — a free-text correlation id stored on the participant for
  the lifetime of the call. Surfaces in participant objects and Event Sink
  payloads. Use it to tie back a participant in Pexip to a row in your
  database.
- **`direct_media`** — declare whether your client supports peer-to-peer
  media. Whether Pexip *uses* direct media is decided by the conference
  configuration; this field just says "I'm capable".
- **`pin`** — the four-or-more-digit PIN. Send the literal string `"none"` if
  you're joining as a guest in a conference where only the **host** role has
  a PIN. Omit the field entirely if there's no PIN at all.
- **`chosen_idp` / `sso_token` / `conference_extension`** — see the flow
  sections below; each is the answer to a previous server-sent prompt.

### The "you must do another step" responses

The endpoint can produce four prompts that look like errors but are actually
control flow. **Don't conflate them with real failures.**

#### a. PIN required (HTTP 403)

```json
{
  "status": "success",
  "result": {
    "pin":       "required",
    "guest_pin": "required" | "none"
  }
}
```

Response says which roles need a PIN. Retry `request_token` with the right
`pin` value (or `"none"` for the no-PIN-role case).

#### b. IDP list (HTTP 200, the `idp` field is the tell)

```json
{
  "status": "success",
  "result": {
    "idp": [
      { "name": "Microsoft Entra ID", "img": "<base64-or-path>", "uuid": "<uuid>" },
      { "name": "ADFS",               "uuid": "<uuid>" }
    ]
  }
}
```

Conference is SSO-protected. Show the IDP list to the user, then retry
`request_token` with `"chosen_idp": "<the-chosen-uuid>"`.

#### c. IDP redirect URL (HTTP 200, the `redirect_url` field is the tell)

```json
{
  "status": "success",
  "result": {
    "redirect_url": "https://idp.example.com/sso?SAMLRequest=…",
    "redirect_idp": { "name": "…", "uuid": "<uuid>" }
  }
}
```

Open the URL in the browser (or in your headless flow). The IDP redirects
back to Pexip with a SAML assertion or JWT. Capture that and retry
`request_token` with `"sso_token": "<assertion>"`.

#### d. Virtual Reception (HTTP 403)

```json
{
  "status": "failure",
  "result": { "conference_extension": "standard" }  // or "mssip"
}
```

The alias is a dispatcher, not a real meeting. Prompt the user for the real
conference alias, then retry `request_token` with
`"conference_extension": "<target_alias>"`.

#### e. Display name required (HTTP 403, post-SSO)

```json
{
  "status": "failure",
  "result": { "display_name": "required" }
}
```

You sent `display_name: false` expecting the IDP to supply it, but it didn't
(or the IDP attribute mapping isn't configured). Retry with a real
`display_name` string.

### Success response (the one you actually want)

```jsonc
{
  "status": "success",
  "result": {
    "token":            "Ohv3IrcV0CJFa…de2PvYam0zqT1G8fEA==",
    "expires":          "120",                   // seconds, as a string
    "participant_uuid": "<uuid>",                // your participant id
    "display_name":     "Alice",                 // may differ if IDP supplied it
    "role":             "HOST" | "GUEST",        // uppercase
    "call_tag":         "ops-bot-7",
    "version":          { "version_id": "41.1", "pseudo_version": "…" },
    "conference_name":  "meet.alice",
    "service_type":         "conference",        // what the alias is configured as
    "current_service_type": "conference"         // what you're in right now
                                                 //   — "waiting_room" when locked + guest
                                                 //   — "ivr" / "gateway" / "test_call" / "connecting"
                                                 //   when relevant
    "call_type":        "video" | "video-only" | "audio",
    "chat_enabled":     true,
    "fecc_enabled":     false,
    "rtmp_enabled":     true,
    "analytics_enabled":true,
    "guests_can_present": true,
    "vp9_enabled":       true,
    "allow_1080p":       true,
    "direct_media":      false,                  // true if the conference is direct-media

    // Direct-media only — present when direct_media is true:
    "pex_datachannel_id":          "42",
    "client_stats_update_interval":"1000",       // ms — POST /statistics this often
    "use_relay_candidates_only":   false,

    // ICE servers for your WebRTC stack (always present):
    "stun": [ { "urls": ["stun:stun.example.com:3478"] } ],
    "turn": [ { "urls": ["turn:turn.example.com:3478?transport=udp"],
                "username": "...", "credential": "..." } ]
  }
}
```

A subtlety worth a callout: **`expires` is a string**, in seconds. Parse to
int before using in arithmetic.

---

## 2. `POST /refresh_token`

Extends the current token's lifetime. Empty body. Token goes in the `token`
header as for any other request.

### Response

```json
{
  "status": "success",
  "result": {
    "token":   "<new token>",
    "expires": "120"
  }
}
```

The new token replaces the old one. The participant UUID and role are
unchanged; nothing about your in-conference state moves.

### Cadence

The docs don't pick a number. **Recommended (common pattern):** refresh at
roughly half of `expires` — so for the typical 120s token, refresh every
60s. That way a single network blip doesn't drop you. Hold one refresh task
per session; never let two refreshes overlap (the new token replaces the
old; concurrent refreshes race and one will fail).

### What happens if you let it expire

Pexip will eventually treat the token as invalid. Subsequent requests fail
(commonly 401 / 403; the exact response isn't documented). On the SSE
stream, the connection drops. **Recovery requires a fresh `request_token`**,
not `refresh_token` — at that point the old token is gone. Your participant
in the conference may or may not also disconnect depending on timing; in
many deployments the participant's media outlives the token by a few
seconds, but you can't rely on that.

---

## 3. `POST /release_token`

Tells Pexip you're done. Empty body, token in `token` header.

The response is best ignored (docs literally say so). After this call:

- Your participant is removed from the conference.
- An `eventsink_*` participant_disconnected event fires (if Event Sink is
  configured).
- The token is no longer valid.

Call this on graceful shutdown. Don't bother if the process is being
killed; Pexip will time out the participant on its own. Calling it twice is
harmless.

---

## 4. The auth header

For every request **except** `request_token`:

```
token: <token value>
```

Header name is literally `token`. Not `Authorization`. Not `X-Pexip-Token`.

For the SSE `/events` endpoint, browsers can't set custom headers on
`EventSource`, so the token goes in the query string instead:

```
GET /api/client/v2/conferences/<alias>/events?token=<token>
```

Pexip accepts either form for `/events`; for everything else, use the
header.

---

## 5. The full join state machine

Bringing the prompts together — what a robust `request_token` loop looks
like (Python-style pseudocode):

```python
def join(node, alias, display_name, pin_callback, sso_callback):
    body = {"display_name": display_name}
    while True:
        r = post(f"{node}/api/client/v2/conferences/{alias}/request_token", json=body)
        result = r.json()["result"]

        if "token" in result:
            return result                                      # ← we're in

        if isinstance(result, dict) and result.get("pin") == "required":
            body["pin"] = pin_callback(result.get("guest_pin"))
            continue

        if isinstance(result, dict) and "idp" in result:
            chosen = sso_callback("choose_idp", result["idp"])
            body["chosen_idp"] = chosen
            continue

        if isinstance(result, dict) and "redirect_url" in result:
            body["sso_token"] = sso_callback("complete_idp", result["redirect_url"])
            continue

        if isinstance(result, dict) and "conference_extension" in result:
            body["conference_extension"] = sso_callback("pick_target", result["conference_extension"])
            continue

        if isinstance(result, dict) and result.get("display_name") == "required":
            body["display_name"] = sso_callback("ask_name", None)
            continue

        raise RuntimeError(f"unexpected request_token response: {result}")
```

The same shape works in TypeScript. The full Python and TypeScript
implementations are in `examples/`.

---

## 6. Edge cases worth knowing

- **Waiting room.** If the conference is locked and you join as guest, the
  token is issued, but `current_service_type` is `"waiting_room"`. The SSE
  stream connects fine, but almost every control endpoint will fail. Watch
  for a `participant_update` event for yourself that flips
  `current_service_type` to `"conference"` — that's when you've been
  admitted.

- **Test call.** Some aliases route to a test-call service (echo/loopback).
  `service_type` will be `"test_call"`. Useful for client self-tests; not
  useful for control flows.

- **Connecting.** Briefly, immediately after token issuance,
  `current_service_type` may be `"connecting"`. Usually flips to
  `"conference"` within a second. If your code depends on the final state,
  wait for the first `conference_update` SSE event, or poll
  `/conference_status` once.

- **`fecc_enabled`** is the conference's view; whether *your* client can
  send FECC depends also on `fecc_supported: true` in your `/calls`
  request.

- **`call_tag` lifetime.** Lives until the participant disconnects. Surfaces
  in the participant object (visible via `/participants` and SSE), in
  `participant_update` events, and in Event Sink payloads. Great breadcrumb.
