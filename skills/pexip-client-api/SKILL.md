---
name: pexip-client-api
description: >
  Expert knowledge for designing, building, and operating applications against
  the **Pexip Infinity Client REST API** — the token-based HTTP+SSE protocol
  spoken by every endpoint and bot that joins a Pexip meeting (browsers,
  mobile, kiosks, recorders, transcribers, dial-out automations, live
  dashboards). Use this skill whenever the user is working with
  `/api/client/v2/conferences/<alias>/…`, the `request_token` / `refresh_token`
  / `release_token` lifecycle, the `/events` Server-Sent Events stream,
  WebRTC media negotiation via `/calls` (`new_offer`, `update_sdp`,
  `new_candidate`, `ack`), direct-media vs transcoded conferences, breakout
  rooms via the client API, host vs guest control actions (lock, mute,
  layout, recording, classification), participant control (transfer, role,
  spotlight, DTMF, FECC), conference dashboards driven by SSE, or
  participant-list reconciliation via `participant_sync_begin`/
  `participant_sync_end`. Also triggers for questions about PexRTC vs the
  raw API, token expiry / reconnect strategy, multi-node Conferencing Node
  failover from a client perspective, virtual-reception / IDP-SSO join
  flows, and the difference between the Client API and the Management
  API. Use this skill — the Client API has subtle lifecycle rules (token
  refresh cadence, sync-bracket semantics, direct-media flow ordering)
  that the docs leave implicit and that bite first-time implementers.
---

# Pexip Infinity Client REST API — Expert Skill

Practical knowledge for building applications against the **Pexip Infinity
Client REST API** (v2) — the protocol every Pexip endpoint uses to authenticate,
control a conference, and (optionally) negotiate WebRTC media. The same API
backs three very different application shapes:

| Shape | Touches | Typical use |
|---|---|---|
| **Control client** | `request_token` → REST POSTs → `release_token` | Backend automation: dial out a participant, set layout, mute guests, send a banner message, lock the room, harvest a participant list. No media. |
| **SSE monitor** | `request_token` → `/events` (SSE) → REST GETs | Real-time dashboards, conference state observers, bots that react to participants joining/leaving, captioning capture, recorders that wake on `conference_started`. |
| **Full client** | All of the above **plus** `/calls` lifecycle (SDP/ICE/ack), `/participants/<uuid>/statistics` | Real client that joins as a real participant with audio/video — custom WebRTC clients, transcribers that consume media, kiosk apps. |

This skill covers all three. The reference files in `references/` go deep on
specific surfaces; this SKILL.md covers the shared model and the operational
patterns that keep an integration trustworthy over time.

> **Sourcing:** the canonical API reference is
> `https://docs.pexip.com/beta/api_client/api_rest.htm`. Where this skill states
> something the docs don't (e.g. recommended refresh cadence, reconnect
> behaviour, how to bracket a roster rebuild around `participant_sync_*`),
> it is marked **⚠️ verify against your version** or **(common pattern)**.

---

## Quick Decision Tree

| Goal | Read first |
|---|---|
| Get a token from `request_token` (PIN, SSO, virtual-reception flows) | `references/token-lifecycle.md` |
| Drive conference-level actions (lock, mute, dial, layout, message) | `references/conference-control.md` |
| Drive per-participant actions (mute, role, transfer, DTMF, spotlight) | `references/participant-control.md` |
| Consume the `/events` Server-Sent Events stream | `references/events-sse.md` |
| Negotiate WebRTC media (`/calls`, `/ack`, `/new_candidate`, `/update`) | `references/calls-media.md` |
| Create/manage breakout rooms | `references/breakouts.md` |
| Understand error responses and edge cases | `references/errors-and-gotchas.md` |
| Build a Python control client end-to-end | §3 + `examples/python_control_client.py` |
| Build a TypeScript SSE listener end-to-end | §4 + `examples/typescript_sse_listener.ts` |

Pattern-level guidance (token refresh, reconnect, idempotency, multi-node) lives
below in §5–§7.

---

## 1. How the Client API Is Shaped

### Base URL and version

```
https://<node_address>/api/client/v2/conferences/<conference_alias>/<request>
```

- **`<node_address>`** is the FQDN or IP of a **Conferencing Node** (not the
  Management Node — that's a different API on a different host). HTTPS only in
  production. The node certificate must be trusted by the client.
- **`<conference_alias>`** is the meeting alias as configured in Pexip (`meet.alice`,
  `meet@example.com`, `+15551234`, etc.). Aliases can contain `@` and other
  characters — URL-encode if your HTTP client doesn't do so transparently.
- **`/api/client/v2/`** is the current major version. Pexip evolves it between
  Infinity releases — fields are added, occasionally renamed. Treat unknown
  response fields as forward-compatible (ignore them) and unknown event names
  the same way; this is how the docs themselves talk about backward
  compatibility.

There is one non-conference endpoint that lives a level higher:

```
GET https://<node_address>/api/client/v2/status     # maintenance check
```

### Response envelope

Every API response (success or failure) is JSON with this envelope:

```json
{ "status": "success", "result": <payload> }
```

| Field | Notes |
|---|---|
| `status` | `"success"` if Pexip processed the command; `"failure"` if it didn't. |
| `result` | On success, the actual payload (object/array/scalar/boolean). On failure, a short reason string. |

Two known oddities to be aware of:

- The `/status` maintenance response uses `"status": "failed"` (past tense) when
  the node is in maintenance — different from `"failure"` elsewhere. Match both
  if you key on it.
- Some error cases return a 4xx HTTP code *and* a JSON envelope with structured
  fields in `result` (PIN required → `403` + `{"pin": "required", "guest_pin": …}`;
  virtual reception → `403` + `{"conference_extension": "standard"|"mssip"}`;
  SSO → `200` + `{"idp": [...]}`). You must inspect the body to decide what to
  do next, not just the status code.

### Authentication header

Every request after `request_token` carries the token in an HTTP header:

```
token: Ohv3IrcV0CJFa…de2PvYam0zqT1G8fEA==
```

Note: it's a custom header literally named `token` — **not** `Authorization`,
not `X-Pexip-Token`. For the SSE `/events` stream, where browsers can't set
custom headers on `EventSource`, the token goes in the query string instead:
`/events?token=<token>`. Either is accepted by Pexip.

### Conference alias model

A single conference alias resolves to a Pexip *service* — which can be a
regular VMR, a Virtual Reception (IVR-style alias dispatcher), a gateway call,
a test call, or a waiting-room landing. The `request_token` response tells you
which kind:

```jsonc
"service_type":         "conference",   // the configured kind
"current_service_type": "waiting_room"  // the kind you are currently in
```

Mostly these match (`conference` / `conference`). They diverge when:

- The conference is locked and you joined as a guest → `current_service_type` is
  `"waiting_room"`. You'll be moved to `"conference"` when the host unlocks or
  admits you (you'll see `current_service_type` change via the next
  `participant_update` for yourself, or you'll have been issued a fresh token).
- The alias is a Virtual Reception. The first `request_token` returns
  `403` + `{"conference_extension": "standard"|"mssip"}`. You must call
  `request_token` again with `"conference_extension": "<target_alias>"` to get
  the token for the real room.
- The alias resolves to a gateway call → `service_type` is `"gateway"`.

> ⚠️ Always branch on `current_service_type` when rendering UI or deciding what
> control actions are valid — a token issued against a `waiting_room` can do
> almost nothing useful until the participant is admitted.

---

## 2. Token Lifecycle in 60 Seconds

The full reference is in `references/token-lifecycle.md`. The minimum you need:

```
POST /request_token        body: { "display_name": "Alice", "pin": "1234" (if needed) }
  ↓
{ token: "...", expires: "120", role: "HOST"|"GUEST",
  current_service_type: "...", direct_media: bool,
  stun: [...], turn: [...] (if direct media), ... }
  ↓
POST /refresh_token        (every ~ expires/2 seconds — see §5)
  ↓
{ token: "<new>", expires: "120" }
  ↓
POST /release_token        (on graceful disconnect)
```

Three things people get wrong on the first attempt:

1. **`expires` is a string, in seconds.** Parse to int. Default is short
   (typically 120s). You will refresh many times in a long meeting.
2. **`request_token` is also the SSO/Virtual-Reception entry point.** A
   non-success body doesn't always mean failure — it may be telling you to
   take another step. Decision-tree pattern (PIN → IDP list → IDP redirect →
   conference extension → display_name) is in `references/token-lifecycle.md`.
3. **PIN with `"none"` is a real value.** If a conference requires a PIN for
   the host role only and you're joining as a guest, you must literally send
   `"pin": "none"` — omitting the field gets you a 403. Conversely, if the
   conference requires no PIN at all, omit the field entirely.

---

## 3. Pattern A — Control Client (No Media)

The simplest shape. Get a token, drive REST actions, release. Useful for ops
tooling, scheduled automations, and CLI utilities.

### Python (httpx, synchronous, the bare minimum)

```python
import httpx, time

NODE  = "https://conf.example.com"
ALIAS = "ops_room"

def request_token(display_name, pin=None):
    body = {"display_name": display_name}
    if pin is not None:
        body["pin"] = pin
    r = httpx.post(f"{NODE}/api/client/v2/conferences/{ALIAS}/request_token", json=body, timeout=15)
    r.raise_for_status()
    return r.json()["result"]

def call(token, path, body=None):
    r = httpx.post(
        f"{NODE}/api/client/v2/conferences/{ALIAS}/{path}",
        json=body or {},
        headers={"token": token},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()

def refresh(token):
    r = httpx.post(f"{NODE}/api/client/v2/conferences/{ALIAS}/refresh_token",
                   headers={"token": token}, timeout=15)
    r.raise_for_status()
    return r.json()["result"]

def release(token):
    httpx.post(f"{NODE}/api/client/v2/conferences/{ALIAS}/release_token",
               headers={"token": token}, timeout=15)

# Drive it.
sess  = request_token("Ops Bot")
token = sess["token"]
try:
    call(token, "lock")
    call(token, "muteguests")
    call(token, "set_message_text", {"text": "Meeting starting"})
    # ... do work ...
finally:
    release(token)
```

For a long-lived control session you must add a refresh loop. The end-to-end
example (with refresh + structured error handling) is in
`examples/python_control_client.py`.

### TypeScript (Node 20+ with fetch)

```typescript
const NODE  = "https://conf.example.com";
const ALIAS = "ops_room";
const BASE  = `${NODE}/api/client/v2/conferences/${encodeURIComponent(ALIAS)}`;

async function requestToken(displayName: string, pin?: string) {
  const r = await fetch(`${BASE}/request_token`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ display_name: displayName, ...(pin && { pin }) }),
  });
  const json = await r.json();
  if (json.status !== "success") throw new Error(`request_token failed: ${JSON.stringify(json)}`);
  return json.result;
}

async function call(token: string, path: string, body: unknown = {}) {
  const r = await fetch(`${BASE}/${path}`, {
    method: "POST",
    headers: { "content-type": "application/json", token },
    body: JSON.stringify(body),
  });
  const json = await r.json();
  if (json.status !== "success") throw new Error(`${path} failed: ${JSON.stringify(json)}`);
  return json.result;
}
```

The full TypeScript control example (with refresh timer + abort handling)
is in `examples/typescript_control_client.ts`.

---

## 4. Pattern B — SSE Monitor

For dashboards, recorders, transcript collectors, and "react when X happens"
bots. You don't need to send media — you just want to observe.

### The connection

```
GET https://<node>/api/client/v2/conferences/<alias>/events?token=<token>
Accept: text/event-stream
```

The stream is **standard EventSource**: `data:` lines (JSON) preceded by
`event:` lines naming the event type, separated by blank lines.

```
event: participant_create
data: {"uuid": "abc…", "display_name": "Alice", "role": "chair", …}

event: layout
data: {"view": "1:7", "participants": ["abc…", "def…"], …}
```

### The single rule that matters: the sync bracket

On every connect — including on every reconnect — Pexip emits a **roster
snapshot** bracketed by two marker events:

```
event: participant_sync_begin
data: 

event: participant_create
data: {"uuid": "abc…", …}      ← participant 1 of N

event: participant_create
data: {"uuid": "def…", …}      ← participant 2 of N

event: participant_sync_end
data: 

event: participant_update       ← from here on it's live deltas
data: {…}
```

Between `participant_sync_begin` and `participant_sync_end`, the
`participant_create` events are **snapshot rows**, not new joins. Treat them as
"this participant is currently in the conference" and **upsert** them into
your roster. After `participant_sync_end`, subsequent `participant_create` /
`_update` / `_delete` are **live deltas**.

A robust pattern (common but not from the docs):

1. On any new SSE connection, clear (or mark stale) your roster.
2. While in the sync bracket, populate it from the snapshot rows.
3. At `participant_sync_end`, swap your roster atomically — anything you
   marked stale and didn't see again is gone.
4. From then on, apply deltas live.

This means **you don't have to call `/participants` on reconnect** — the SSE
stream re-bootstraps you for free. (You *can* call `/participants` for
out-of-band snapshots, but you generally shouldn't need to.)

### What's missing from the SSE protocol (and what to do about it)

The docs are silent on several operational details. From observation /
common practice:

| Concern | Reality | What to do |
|---|---|---|
| **Last-Event-ID / replay** | Not supported. Reconnects start fresh — that's what the sync bracket exists for. | Don't try to resume. Always re-bootstrap from `participant_sync_*`. |
| **Heartbeat** | Not documented. | Set a watchdog: if you receive nothing (no event, no comment line) for N seconds (60–120s is a reasonable default), assume the connection is dead, close it, reconnect with backoff. |
| **Reconnect backoff** | Not documented. | Exponential with jitter, capped (e.g. 1s → 2s → 4s → … → 30s max). On 401 (token expired), `request_token` again before reconnecting. |
| **Token refresh during the stream** | No in-stream refresh mechanism. | Refresh the token on a separate timer in the background; the same token continues to authorize the existing SSE connection until it expires. ⚠️ Verify on your version — some sites report that an SSE connection authenticated with a refreshed-away token can keep working until idle-close, others see immediate cut. Plan to **reconnect after refresh** if you observe drops. |
| **Multi-node** | Each conference can span multiple Conferencing Nodes. The SSE stream you're connected to is per-node. | A bot that wants a global view should pin to one node (or connect to several and merge by `participant.uuid`). Usually one node is fine; the node Pexip routed you to has the canonical view of *this* token's session. |

### Skeleton (Python, async, with reconnect)

```python
import asyncio, json, httpx

async def listen(node, alias, token, handle):
    """Consume the SSE stream; call handle(event_name, data_dict)."""
    url = f"{node}/api/client/v2/conferences/{alias}/events?token={token}"
    backoff = 1.0
    while True:
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("GET", url, headers={"Accept": "text/event-stream"}) as r:
                    r.raise_for_status()
                    backoff = 1.0
                    event_name = None
                    async for line in r.aiter_lines():
                        if line.startswith("event:"):
                            event_name = line[6:].strip()
                        elif line.startswith("data:"):
                            data = line[5:].strip()
                            payload = json.loads(data) if data and data != "null" else None
                            await handle(event_name, payload)
                            event_name = None
                        elif line == "":  # message terminator
                            event_name = None
        except (httpx.HTTPError, asyncio.CancelledError):
            raise
        except Exception:
            await asyncio.sleep(min(backoff, 30))
            backoff *= 2
```

The full version (with token refresh, watchdog timeout, sync-bracket
tracking, and a 401-aware re-auth path) is in
`examples/python_sse_listener.py`. The TypeScript equivalent is in
`examples/typescript_sse_listener.ts`.

---

## 5. Pattern C — Full Media Client

For real WebRTC participants — custom clients, recorders that ingest media,
transcribers. This is the heaviest path and the one most worth reading
`references/calls-media.md` for in full.

### The two media modes

| Mode | When | Flow |
|---|---|---|
| **Transcoded** | `request_token` response has `direct_media: false` (or omitted). Pexip composes media centrally. | Send local SDP offer → get answer immediately → ICE → `/ack` → media. |
| **Direct media** | `request_token` response has `direct_media: true`. Peer-to-peer media between two participants on one conference; CPU saved on the node. | Send local SDP offer → **may receive empty answer** → wait for `new_offer` event → answer → `/ack` → ICE via `new_candidate` events both ways → media. |

Direct media is the one that bites first-time implementers because the flow
is reactive — you don't drive it, you respond to events. Section
`references/calls-media.md` walks the full state machine. Three things to
internalise up front:

1. **An empty `sdp` in the `/calls` response is not an error.** In direct
   media mode it means "far end not ready yet, wait for the `new_offer`
   event". Don't call `/ack`. Don't time out aggressively.
2. **`/ack` means "I have media set up, start the flow"** — it's the trigger
   to start the actual RTP, not an HTTP-level acknowledgement.
3. **`/participants/<uuid>/statistics`** is only used in direct-media mode
   (the node can't see the media, so you tell it). Send at the
   `client_stats_update_interval` declared in `request_token`. Transcoded
   calls leave this endpoint alone.

### Presentation (screenshare) in one paragraph

To **send** a presentation, your endpoint negotiated 3 m-lines in the
original `/calls` SDP (audio + video + presentation, marked with
`a=content:slides`), then you `POST /participants/<uuid>/take_floor`. When
done, `POST /participants/<uuid>/release_floor`. To **receive** presentation,
either include the third m-line in your offer (separate stream) or send
`/calls` with `"present": "main"` to swap presentation in place of the main
video (single stream — useful for low-bandwidth clients). The
`presentation_frame` SSE event is a poll trigger, not a payload — when it
fires, fetch the JPEG from `/presentation.jpeg` (or `/presentation_high.jpeg`)
with the token. This is useful even for non-media clients that want to
capture slide snapshots.

---

## 6. Production Patterns

### 6.1 Token refresh — what cadence?

The docs say the token has an `expires` value (in seconds), typically 120,
and that you must call `refresh_token` before it expires. They don't pick a
cadence. **Common practice:** refresh at roughly half the `expires` value —
e.g. every 60s for a 120s token — so a single missed refresh doesn't drop
the session. Hold a single refresh task per session, never refresh from
multiple coroutines/threads concurrently (the new token replaces the old;
overlapping calls race).

After a successful refresh:

```python
session["token"] = new_token   # all subsequent calls use this
```

`refresh_token` does **not** affect your `participant_uuid`, role, or any
in-conference state. It's just a new bearer.

### 6.2 Reconnect strategy for the SSE stream

```
connect → on disconnect/timeout/4xx → backoff with jitter
                                      → if 401: request_token again first
                                      → reconnect → sync-bracket re-bootstraps
```

Two practical knobs:

- **Idle timeout / watchdog.** Reset a timer on every received byte (event,
  comment, or even just a newline). If it fires without data, `close()` the
  connection — TCP keepalives alone aren't fast enough.
- **Backoff cap.** 30s is plenty. The connection is cheap; you want fast
  recovery, not fairness with the server.

### 6.3 Idempotency of control actions

Most of the control endpoints are naturally idempotent at the conference
level — `lock` on an already-locked conference is a no-op, `mute` on a
participant who's already muted is a no-op. A few aren't:

- **`message` / `set_message_text`** — sending the same chat message twice
  delivers it twice. If your control loop retries after a network blip,
  deduplicate at your side (e.g. don't retry POSTs that *might* have
  succeeded — re-check state with a GET first if it matters).
- **`dial`** — each call creates a new participant. Retrying a flaky dial
  can produce two phantom participants. Wait long enough for the first one
  to either show up in the participant list or fail; only then retry.
- **`breakouts` (create)** — creates new rooms; retry produces duplicates.

### 6.4 Host vs Guest in your code

The `request_token` response includes `"role": "HOST"` (alias `chair`) or
`"role": "GUEST"`. Most control endpoints (lock, dial, mute everyone, set
layout, kick someone) require Host. The docs flag which endpoints are
host-only; if you call one as a guest you get a failure response — handle
it in your error path. A bot/control client should join with a host PIN
so it has the permissions it needs; alternatively, a bot can hold its own
service-user identity through IDP-issued attestation.

### 6.5 Conference identity across multiple nodes

A conference may be hosted on several Conferencing Nodes simultaneously (one
per location, for instance). The Client API token you hold is bound to **one
participant on one node**. Implications:

- `/conference_status` returns *this node's* view. For most purposes it's
  the same as the global view, but if you have a strong consistency need,
  reconcile across multiple sessions.
- `participant_create` / `_update` / `_delete` on your SSE stream cover
  every participant, regardless of which node they're on — Pexip
  synchronises participant state across nodes.
- The `presentation_frame` JPEG is served by *your* node; in pathological
  network situations it can lag the actual presentation by hundreds of
  milliseconds.

### 6.6 Choosing a Conferencing Node from a client

There's no auto-discovery endpoint in the Client API itself. Clients
typically pick a node via:

- A DNS A record pointing at a load balancer / Pexip's locator.
- A specific node FQDN baked into config.
- A custom node-selector service you run that returns "this is the best node
  for you right now" (e.g. by geo).

For a control/automation client this is usually a single hardcoded address.
For a real client, follow Pexip's recommended deployment pattern for your
topology.

### 6.7 Logging that's useful when things break

Per request: log the request line + the **status** field of the response
(success/failure) + the **time taken**. Don't log the token. On failure,
log the `result` field — that's the reason string.

Per SSE: log every reconnect with the reason (timeout, 401, peer-reset,
server-close) plus the count of events received during the prior session.
That's enough to catch a "we're losing the stream every 90 seconds" issue
without drowning in `participant_update` noise.

---

## 7. Common Gotchas

A short list — the long list is in `references/errors-and-gotchas.md`.

1. **`Authorization: Bearer` does not work.** The Client API uses a header
   literally called `token`. Easy to mistype on day one.

2. **`request_token` can return HTTP 200 with `status: success` but be telling
   you "go authenticate elsewhere"** (the IDP-list case). Read the body,
   not just the status code.

3. **`refresh_token` does not extend the SSE connection lifetime.** It just
   keeps the *token* alive. The SSE TCP connection lives until something
   kills it — a network event, a server-side restart, or token expiry. Run
   the refresh independently and reconnect SSE on any drop.

4. **`participant_sync_begin` arrives even when nothing's changed** — every
   new SSE connection sends one. Don't treat its arrival as a meaningful
   event for your business logic; treat the contents of the bracket as a
   roster snapshot.

5. **`participant_update` repeats the full participant object, every time.**
   It's not a delta. If you're storing change history, diff against your
   previous copy yourself.

6. **A locked conference + a guest join = a `current_service_type` of
   `"waiting_room"`.** The token is real and the SSE stream works, but
   nearly all control endpoints will fail until the host admits you. Branch
   on `current_service_type`, not on the presence of the token.

7. **`message` is *not* the same as `chat` to the user.** The `message`
   endpoint sends what the user perceives as a chat message; the
   `set_message_text` endpoint sets a banner across the stage. Different
   APIs, different UX, easy to confuse.

8. **`role: "HOST"` in the token response but `role: "chair"` in the
   participant object.** Yes, really. They mean the same thing.
   `"HOST"`/`"GUEST"` (uppercase) is the token-response vocabulary;
   `"chair"`/`"guest"` (lowercase) is the participant-object vocabulary.
   Cross-reference accordingly.

9. **Conference aliases with `@` and `+` need URL encoding** in the path
   (or your HTTP client must encode for you). Some libraries don't encode
   `@` by default.

10. **A 503 from `/status` means the node itself is in maintenance**, not
    that the conference is down. Useful as a pre-flight from a client that
    can fail over to another node.

---

## 8. The Client API vs the Other Pexip APIs

| API | Surface | Use case |
|---|---|---|
| **Client API** *(this skill)* | `/api/client/v2/conferences/<alias>/…` | Anything participant-facing. Tokens. Per-meeting state. WebRTC. SSE events. |
| **Management API** | `/api/admin/configuration/v1/…`, `/api/admin/status/v1/…` | Provisioning VMRs, system status, locations, licences, participant *administrative* view (drop a participant from outside the meeting). Lives on the Management Node, not Conferencing Nodes. |
| **Event Sink** | Push from Pexip to your webhook | Fire-and-forget CDR / billing / analytics ingest. See the `pexip-event-sink` skill. |
| **External Policy** | Pull from Pexip during call setup | Synchronous policy decisions (who's allowed, what VMR, what role). See the `pexip-external-policy` skill. |

A typical "watch a conference" tool uses the **Client API SSE stream**, not
the Event Sink — they're different shapes (interactive vs fire-and-forget)
and the Client API is bound to one alias at a time.

A typical "drop a runaway participant from outside the meeting" tool uses
the **Management API**, not the Client API — you don't have a token in
that conference.

### PexRTC

Pexip ship a JavaScript wrapper called **PexRTC** at
`https://<node>/static/webrtc/js/pexrtc.js` that abstracts the WebRTC media
parts of the Client API (SDP, ICE, ack, presentation, FECC) and exposes a
callback-based API. It's the path of least resistance for a browser-based
custom client and is what Pexip recommends for web apps. This skill focuses
on the raw API because:

- PexRTC is browser-only (no Node, no Python).
- The protocol underneath is what you need to know to debug it.
- Non-browser clients (servers, native apps, transcribers) will speak the
  raw API regardless.

If the user is building a web app and PexRTC fits, *use it*. The skill is
here to fall back on when you need to look under the hood.

---

## 9. Reference index

| File | Covers |
|---|---|
| `references/token-lifecycle.md` | `request_token` / `refresh_token` / `release_token` in full, including PIN, IDP/SSO, Virtual Reception, and the full set of fields in the token response. |
| `references/conference-control.md` | Every conference-level POST/GET — lock, dial, mute, layout, banners, timer, classification, pinning, themes, etc. Body and response shapes. |
| `references/participant-control.md` | Every per-participant endpoint, plus the full participant-object field reference (40+ fields). |
| `references/events-sse.md` | The SSE stream in detail: every event type, its payload, its trigger. Reconnect/sync-bracket semantics. |
| `references/calls-media.md` | WebRTC negotiation via `/calls`. Transcoded vs direct-media state machines. Presentation, FECC, stats. |
| `references/breakouts.md` | Breakout-room creation, transfer, leave; the host-side `breakout_*` SSE events. |
| `references/errors-and-gotchas.md` | Error envelope, status codes, alias encoding, multi-node, version-skew compatibility, the long list of "I tripped over this once". |

Each reference is self-contained — read SKILL.md for the model, then jump
into whichever reference matches your task.
