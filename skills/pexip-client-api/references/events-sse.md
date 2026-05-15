# Events — Server-Sent Events Stream Reference

Real-time updates from a Pexip Conferencing Node to a connected client. One
SSE connection per token. Everything you see on stage, every state change,
and (in direct-media mode) all of the media-negotiation signalling arrives
on this stream.

---

## Connecting

```
GET /api/client/v2/conferences/<alias>/events?token=<token>
Accept: text/event-stream
```

The token may be passed via the `token` query parameter (always works,
including from `EventSource` in browsers) or via the `token` HTTP header
(only available from non-browser clients).

The response is a standard SSE stream:

```
event: <event_name>
data: <json>

event: <event_name>
data: <json>

```

(Each event terminated by a blank line.)

Most events carry a JSON object on `data`; a few have no payload, in which
case the `data:` line is empty or absent.

### What's *not* documented (and is operationally important)

| Concern | Reality |
|---|---|
| Last-Event-ID / replay | **Not supported.** Reconnects start fresh. The `participant_sync_*` bracket exists exactly to re-bootstrap state on every reconnect. |
| Heartbeat / keepalive | **Not specified.** Set a client-side watchdog (60–120s without bytes → reconnect). |
| Ordering across events | Implied in-order on a single connection. No global ordering guarantees if you're observing across nodes. |
| Sequence numbers / event IDs | **None.** No way to correlate or reorder; trust per-connection order only. |
| Token refresh effect on the stream | Not documented. Common observation: refreshing the token does **not** terminate the existing stream; reconnect with the new token only if the existing one drops. ⚠️ Verify in your version. |

---

## The sync bracket — read this before anything else

Every new SSE connection (including every reconnect) opens with:

```
event: participant_sync_begin
data:

event: participant_create
data: {…participant object…}

event: participant_create
data: {…}

  …possibly other events…

event: participant_sync_end
data:
```

Between `participant_sync_begin` and `participant_sync_end`, each
`participant_create` event is a **snapshot row**, not a "someone just
joined" event. After `participant_sync_end`, subsequent
`participant_create`/`participant_update`/`participant_delete` events are
**live deltas**.

A robust roster-tracker:

```python
in_sync   = False
roster    = {}                    # uuid → participant
seen      = set()                 # uuids seen during sync

def on_event(name, data):
    global in_sync, roster, seen
    if name == "participant_sync_begin":
        in_sync = True
        seen = set()
    elif name == "participant_sync_end":
        in_sync = False
        # drop anyone we didn't see
        roster = {u: p for u, p in roster.items() if u in seen}
    elif name == "participant_create":
        roster[data["uuid"]] = data
        if in_sync:
            seen.add(data["uuid"])
    elif name == "participant_update":
        roster[data["uuid"]] = data
    elif name == "participant_delete":
        roster.pop(data["uuid"], None)
```

This is the canonical pattern. Don't call `GET /participants` on reconnect
— the bracket already gives you a clean re-bootstrap.

---

## Event catalogue

### Conference & sync

| Event | Trigger | Payload (key fields) |
|---|---|---|
| `participant_sync_begin` | Every (re)connect | empty |
| `participant_sync_end` | After the snapshot | empty |
| `conference_update` | Conference state changed | see below |
| `layout` | Stage layout changed | see below |
| `stage` | Active-speaker order changed | array; see below |
| `message_received` | Chat message broadcast or direct | see below |
| `splash_screen` | Client should display/clear a splash | `{"screen_key": "…"}` or null |
| `refer` | Client should join a different alias | `{"alias":"<target>","breakout_name":"…"}` |
| `disconnect` | Pexip is dropping you | `{"reason":"…"}` |

### Participants

| Event | Trigger | Payload |
|---|---|---|
| `participant_create` | Snapshot or new join | full participant object (see `participant-control.md`) |
| `participant_update` | Properties changed | full participant object (not a diff) |
| `participant_delete` | Participant left | `{"uuid": "<uuid>"}` |

### Presentation

| Event | Trigger | Payload |
|---|---|---|
| `presentation_start` | Someone started presenting | `{"presenter_name":"…","presenter_uri":"…","source":"video"\|"static"}` |
| `presentation_stop` | Presentation ended | empty |
| `presentation_frame` | A new frame is ready | empty — *fetch* from `/presentation.jpeg` |

### Live captions

| Event | Trigger | Payload |
|---|---|---|
| `live_captions` | Caption text for this participant (after `show_live_captions`) | `{"data":"hello world","is_final":true,"src_lang":"en-US","tgt_lang":"en-US","sources":[{"participant_uuid":"…"}]}` (`sources` is tech preview) |

### Direct-media WebRTC

| Event | Trigger | Payload |
|---|---|---|
| `new_offer` | Far end sent an SDP offer | `{"sdp":"…"}` |
| `update_sdp` | Far end sent an SDP update (ICE restart) | `{"sdp":"…"}` |
| `new_candidate` | Trickle ICE candidate from far end | `{"candidate":"…","mid":"…","ufrag":"…","pwd":"…"}` |
| `peer_disconnect` | Far end participant left | empty |
| `call_disconnected` | A child call (e.g. presentation) was disconnected | `{"call_uuid":"…","reason":"…"}` |

### Breakouts (host's main-room stream)

| Event | Trigger | Payload |
|---|---|---|
| `breakout_begin` | Breakout room created | `{"breakout_uuid":"…","participant_uuid":"<your control participant in that breakout>"}` |
| `breakout_event` | Sub-event inside a breakout | `{"breakout_uuid":"…","event":"<inner event name>","data":{…inner data…}}` |
| `breakout_end` | Breakout closed | `{"breakout_uuid":"…","participant_uuid":"…"}` |
| `breakout_refer` | Move your media to a different breakout | `{"breakout_uuid":"main"\|"<uuid>","breakout_name":"…"}` |

---

## Payload details (the big ones)

### `conference_update`

```jsonc
{
  "locked":                false,
  "guests_muted":          false,
  "all_muted":             false,
  "chat_enabled":          true,
  "presentation_allowed":  true,
  "guests_can_present":    true,
  "guests_can_unmute":     true,
  "started":               true,
  "live_captions_available": false,
  "custom_properties":     null,
  "host_custom_properties":null,
  "direct_media":          false,
  "recording":             false,
  "transcribing":          false,
  "streaming":             false,
  "public_streaming":      false,
  "ai_enabled":            false,
  "external_media_processing": false,
  "classification":  { "levels": {…}, "current": null },
  "message_text":    null,
  "pinning_config":  "default",
  "breakout_rooms":  false,
  "breakout_name":   "",
  "breakout_description": "",
  "end_action":      "transfer",
  "end_time":        1715800000,
  "breakout_guests_allowed_to_leave": true
}
```

Note `host_custom_properties` only appears for hosts; it's `null` for guests
(or omitted, depending on version — handle both).

### `layout`

```jsonc
{
  "view":         "1:7",                       // currently rendered layout name
  "participants": ["<uuid>","<uuid>",…],       // ordered by display position (main speaker first)
  "requested_layout": {                        // what was *requested* (may differ from view)
    "primary_screen": { "chair_layout":"ac","guest_layout":"1:0" }
  },
  "overlay_text_enabled":   true,
  "guests_can_see_guests":  "no_hosts" | "always" | "never"
}
```

`participants` is sometimes empty — for API-only participants with no media,
Pexip sends an empty list. Don't treat it as "conference is empty".

### `stage`

An array, not a wrapped object:

```json
[
  { "stage_index": 0, "participant_uuid": "<uuid>", "vad": 47 },
  { "stage_index": 1, "participant_uuid": "<uuid>", "vad": 0  },
  …
]
```

`stage_index: 0` is the most recent speaker. `vad` is voice-activity-detection
intensity (0–100). Drives "who's currently talking" indicators.

### `message_received`

```jsonc
{
  "origin":   "Alice",
  "uuid":     "<sender uuid>",
  "type":     "text/plain" | "application/json",
  "direct":   false,             // true = private/direct, false = broadcast
  "payload":  "hi everyone"      // always a string; for application/json, parse yourself
}
```

### `splash_screen`

```jsonc
{ "screen_key": "direct_media_welcome"
              | "direct_media_waiting_for_host"
              | "direct_media_other_participants_audio_only"
              | "direct_media_escalate"
              | "direct_media_deescalate" }
```

`null` payload clears the splash. Used in direct-media flows; clients render
the corresponding screen locally (themes are fetched via `/theme`).

---

## Token refresh and the SSE stream

The Client API has no in-stream token refresh mechanism. The pattern is:

1. **Run a refresh timer independently** from the SSE consumer. It hits
   `/refresh_token` every ~ `expires/2` seconds and updates the shared
   token.
2. **Don't reconnect on every refresh.** The existing SSE connection,
   authenticated with the now-replaced token, usually continues to work.
   ⚠️ This is observed behaviour, not promised — verify on your version.
3. **Reconnect on actual drops.** When the stream errors / TCP closes,
   reconnect with the *current* token. If you get a 401, fall back to a
   fresh `request_token`.

---

## Browser `EventSource` notes

Browsers can use the built-in `EventSource(url)` for this stream. Gotchas:

- **You can't set custom headers** on `EventSource`. Token must go in the
  query string. (`new EventSource(url + "?token=" + token)`.)
- **The browser auto-reconnects** on transport errors with a default
  ~3 second retry. For most uses that's fine. If you need finer control,
  manage your own reconnect with `fetch` + a `ReadableStream` reader.
- **`event:` lines are honoured.** Listen with
  `es.addEventListener("participant_create", …)` per event, not just
  `onmessage`.

Sample browser pattern:

```js
const es = new EventSource(`/api/client/v2/conferences/${alias}/events?token=${token}`);

const knownEvents = [
  "participant_sync_begin","participant_sync_end",
  "participant_create","participant_update","participant_delete",
  "conference_update","layout","stage",
  "message_received","presentation_start","presentation_stop","presentation_frame",
  "live_captions","splash_screen","refer","disconnect",
  "new_offer","update_sdp","new_candidate","peer_disconnect","call_disconnected",
  "breakout_begin","breakout_event","breakout_end","breakout_refer",
];

for (const name of knownEvents) {
  es.addEventListener(name, ev => {
    const data = ev.data ? JSON.parse(ev.data) : null;
    handle(name, data);
  });
}

es.onerror = (e) => {
  // EventSource will auto-reconnect; observe + log only.
  console.warn("SSE error", e);
};
```

The non-browser equivalents (Node `fetch` streaming, Python `httpx` streaming)
need manual SSE parsing and reconnect — see `examples/`.

---

## Forward compatibility

Pexip can add new event names between Infinity releases. Always include a
**default branch** in your event dispatcher:

```python
match name:
    case "participant_create":  …
    case "participant_update":  …
    case "participant_delete":  …
    …
    case _:
        log.debug("ignoring unknown event %s", name)
```

Similarly, participant and conference objects may grow fields. Read what
you need; ignore the rest.
