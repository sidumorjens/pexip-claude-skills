# Conference Control — Reference

Endpoints scoped to the conference as a whole (rather than a specific
participant). Most require **Host** role; the few that don't are noted.

All paths are under `/api/client/v2/conferences/<alias>/`. All POSTs accept
an empty body unless a body is shown. All responses are wrapped in
`{"status": ..., "result": ...}`.

---

## State inspection (GET)

### `GET /conference_status`

Returns the current state of the conference. Available to any participant.

```jsonc
{
  "locked":               false,
  "guests_muted":         false,
  "all_muted":            false,
  "chat_enabled":         true,
  "presentation_allowed": true,
  "guests_can_present":   true,
  "guests_can_unmute":    true,
  "started":              true,           // host has admitted/started
  "live_captions_available": false,
  "direct_media":         false,
  "recording":            false,
  "transcribing":         false,
  "streaming":            false,
  "public_streaming":     false,
  "ai_enabled":           false,
  "external_media_processing": false,
  "classification":       { "levels": { "0": "Unclassified", "1": "Official" },
                            "current": null },
  "message_text":         null,            // banner text, if any
  "pinning_config":       "default",
  "breakout_rooms":       false,
  "breakout_name":        "",
  "breakout_description": "",
  "end_action":           "transfer",      // or "disconnect"
  "end_time":             1715800000,
  "breakout_guests_allowed_to_leave": true,
  "custom_properties":      null,          // dict | null
  "host_custom_properties": null           // dict | null (host only)
}
```

This is a snapshot — for live updates, listen for `conference_update` on
the SSE stream (same payload shape).

### `GET /participants`

Returns the live participant roster as an **array**. Each element is the
full participant object documented in `participant-control.md` (§
"Participant object"). Available to any participant.

> ⚠️ For long-running monitors, prefer the SSE `participant_sync_*` bracket
> to a poll loop — see `events-sse.md`.

### `GET /available_layouts`

```json
{ "status": "success",
  "result": ["1:0","1:7","2:21","4:0","9:0","16:0","25:0","ac",…] }
```

With `?annotate=true`, returns objects with metadata tags:

```json
{ "result": [
    { "name": "2x2", "tags": ["equal","has-native-multiscreen"] },
    …
] }
```

### `GET /layout_svgs`

Map of layout name → SVG XML. Useful for rendering a layout picker.

```json
{ "result": { "1:7": "<svg …>…</svg>", "2x2": "<svg …>…</svg>", … } }
```

### `GET /get_message_text`

```json
{ "result": { "text": "Welcome", "set_time": "<ISO timestamp>" } }
```

### `GET /get_clock`

Echoes back the current timer config (`set_clock` body shape; see below).
Empty `result` when no timer is set.

### `GET /get_pinning_config`

```json
{ "result": {
    "pinning_config":      "basic_backfill",
    "pinning_config_dict": { "name": "basic_backfill",
                              "slots": [...],
                              "backfill": true,
                              "remove_self": false } } }
```

### `GET /available_pinning_configs`

```json
{ "result": ["basic_backfill","complex"] }
```

### `GET /get_classification_level`

```json
{ "result": { "levels":  { "0": "Unclassified", "1": "Official", "2": "Secret" },
              "current": 1 } }
```

### `GET /theme`, `GET /theme/<resource_path>`

Returns theme resources (HTML/CSS/images/SVGs) for clients rendering custom
branding locally. Only relevant in direct-media flows where the client owns
rendering. Out of scope for control bots.

### `GET /api/client/v2/status` (not under `/conferences/`)

Maintenance pre-flight. Returns:

```json
{"status":"success","result":"OK"}                          // 200, ready
{"status":"failed","result":"Maintenance mode"}             // 503, do not use
```

Note the `"failed"` (past tense) — this endpoint is inconsistent with the
rest of the API.

---

## Conference lifecycle

### `POST /start_conference`

Starts the conference (admits any guests waiting for host). Idempotent —
no-op if already started.

### `POST /lock` / `POST /unlock`

Toggles `locked`. While locked, new guests land in `current_service_type:
"waiting_room"` instead of `"conference"` until admitted via the
per-participant `unlock` endpoint.

### `POST /disconnect`

Disconnects **all** participants and ends the conference. Strong action;
only use if you mean to terminate the meeting.

---

## Muting & permissions

### `POST /muteguests` / `POST /unmuteguests`

Mute or unmute every guest. Hosts (chairs) are unaffected.

### `POST /set_guests_can_unmute`

```json
{ "setting": true }
```

When `false`, muted guests can't unmute themselves — host-only unmute.

### `POST /set_guests_can_present`

```json
{ "setting": true }
```

Toggles whether guests can grab the presentation floor.

### `POST /set_guests_can_see_guests`

```json
{ "setting": "always" | "no_hosts" | "never" }
```

Virtual Auditorium mode: do guests see other guests in the layout, only
when no hosts are present, or never (auditorium feel)?

---

## Sending things to participants

### `POST /message`

Broadcast chat message.

```json
{ "type": "text/plain", "payload": "Welcome everyone" }
```

Or send structured data:

```json
{ "type": "application/json", "payload": "{\"kind\":\"poll\",\"id\":7}" }
```

Note `payload` is always a string — even for `application/json`, you stringify
yourself.

Arrives at every participant as a `message_received` SSE event.

**Not idempotent** — retrying sends twice. See SKILL.md §6.3.

### `POST /set_message_text`

Sets a persistent banner across the stage.

```json
{ "text": "Webinar starts at 14:00\nPlease keep mics muted" }
```

Replaces the previous banner. Send an empty string to clear.

### `POST /set_clock`

Display a timer on the stage.

```jsonc
{
  "type":           "remaining",        // "remaining" | "elapsed" | "time"
  "starting_value": 300,                // seconds — only for "remaining"
  "prefix":         "Time left: ",
  "suffix":         "",
  "date":           "dd/mm/yyyy"        // only for "time"
}
```

`"remaining"` counts down from `starting_value`. `"elapsed"` counts up
from zero. `"time"` shows current wall-clock time formatted per `date`.

### `POST /dial`

Make Pexip dial *out* to add a participant (PSTN, SIP, H.323, RTMP, MS
Teams, Skype for Business, another VMR).

```jsonc
{
  "destination":          "alice@example.com" | "+15551234567",
  "protocol":             "sip" | "h323" | "rtmp" | "mssip" | "auto",
  "role":                 "GUEST" | "HOST",
  "call_type":            "video" | "video-only" | "audio",
  "source_display_name":  "Pexip Operator",          // shown on callee's screen
  "source":               "sip:bot@example.com",     // SIP From / H.323 source
  "remote_display_name":  "Alice Director",          // overlay name on stage
  "text":                 "Director Alice",          // overlay text override
  "presentation_url":     "rtmp://...",              // RTMP streaming destinations
  "streaming":            "yes" | "no",
  "dtmf_sequence":        "1234#",                   // post-connect DTMF
  "keep_conference_alive": "keep_conference_alive"
                          | "keep_conference_alive_if_multiple"
                          | "keep_conference_alive_never"
}
```

Response:

```json
{ "status": "success", "result": ["<new-participant-uuid>"] }
```

The dialled participant shows up as `participant_create` on the SSE
stream within seconds. **Not idempotent** — retry only after you're sure
the first attempt didn't succeed.

---

## Stage / layout

### `POST /transform_layout`

The kitchen-sink layout endpoint. Body wraps everything in `transforms`:

```jsonc
{
  "transforms": {
    "layout":          "1:7",                 // or any name from /available_layouts
    "host_layout":     "ac",                  // separate layout for hosts (Virt. Auditorium)
    "guest_layout":    "1:0",                 // separate layout for guests (Virt. Auditorium)

    "enable_extended_ac":              true,
    "ai_enabled_indicator":            true,
    "enable_active_speaker_indication":true,
    "enable_overlay_text":             true,
    "external_media_processing_indicator": true,
    "live_captions_indicator":         true,
    "recording_indicator":             true,
    "streaming_indicator":             true,
    "transcribing_indicator":          true,

    "streaming": {                            // distinct layout when streaming/recording
      "layout":                  "1:0",
      "waiting_screen_enabled":  true,
      "indicators_enabled":      true,
      "presentation_in_mix":     true
    },

    "free_form_overlay_text": ["Alice","Bob","Charlie"]   // override participant overlays
  }
}
```

Each field is optional — only include what you want to change.

Emits a `layout` SSE event when the rendered layout actually changes.

### `POST /clearspotlights`

Removes spotlight from all participants. (To spotlight one, use the
per-participant `spotlighton`.)

### `POST /clearallbuzz`

Lowers all raised hands. (To buzz/clearbuzz a single participant, use the
per-participant variants.)

### `POST /silent_video_detection`

```json
{ "setting": true }
```

For Adaptive Composition layouts — drop participants from the mix when
they're silent and have a black/static video. Hosts can override
participant-by-participant.

### `POST /set_pinning_config`

```jsonc
{
  "pinning_config": "basic_backfill",         // a name from /available_pinning_configs
  "dynamic_pinning_config": {                 // OR an inline config
    "name":        "custom-grid",
    "slots":       [ { "layout_groups": ["a"] }, { "layout_groups": ["b","c"] } ],
    "backfill":    true,
    "remove_self": false
  }
}
```

Pinning controls which participants get which display slots regardless of
who's speaking. Useful for scripted broadcasts, panel discussions.

### `POST /video_mixes/create`, `POST /video_mixes/<name>/configure`, `POST /video_mixes/<name>/delete`

Personal video layouts — let a participant see a different mix from the
default. Advanced; rarely needed for control bots.

---

## Recording / streaming / classification

### `POST /set_classification_level`

```json
{ "classification_level": 2 }
```

Sets the active level (must match a key from the conference's classification
levels — see `/get_classification_level`).

### Recording, streaming, AI, transcription toggles

These aren't single dedicated endpoints — they're controlled via
`transform_layout` indicators, the conference configuration (Management
API), or by Pexip features driven from outside the Client API. Inspect
`/conference_status` to see current state; mutate via the appropriate
admin/management surface or per-participant control.

> ⚠️ Verify against your version — some deployments expose recording
> start/stop via the Client API, others only via the Management API.

---

## Breakouts (overview)

`POST /breakouts` creates breakout rooms; the full breakout surface is
covered in `references/breakouts.md`. Brief shape:

```jsonc
{
  "name":     "Discussion 1",
  "duration": 600,                       // seconds; 0 = no auto-end
  "end_action": "transfer" | "disconnect",
  "participants": {
    "main":           ["<uuid>", "<uuid>"],   // who stays in main
    "<breakout-uuid>":["<uuid>", "<uuid>"]   // who goes where
  },
  "guests_allowed_to_leave": true
}
```

---

## Host-only? At a glance

| Endpoint | Role required |
|---|---|
| `conference_status`, `participants`, `available_layouts`, `layout_svgs`, `get_*` | any |
| `lock`, `unlock`, `start_conference`, `disconnect`, `dial` | host |
| `muteguests`, `unmuteguests`, `set_guests_can_*` | host |
| `message`, `set_message_text`, `set_clock` | host |
| `transform_layout`, `clearspotlights`, `clearallbuzz`, `set_pinning_config` | host |
| `set_classification_level` | host |
| `breakouts` (create) | host |

A guest token calling a host endpoint returns
`{"status":"failure","result":"<reason>"}`. The reason string varies by
endpoint; treat all of them as "you don't have permission".
