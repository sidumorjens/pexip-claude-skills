# Participant Control — Reference

Endpoints scoped to a specific participant. All under

```
/api/client/v2/conferences/<alias>/participants/<participant_uuid>/
```

`<participant_uuid>` is the participant's `uuid` (as it appears in the
participant object / SSE events). Your own UUID is in the `request_token`
response as `participant_uuid`.

Most participant control endpoints require Host (`role: chair`) to act on
*other* participants. A participant can always act on themselves
(self-mute, self-leave, change their own overlay text in some setups, etc.).

---

## The participant object

Returned by `GET /participants` (as array elements), by
`GET /participants/<uuid>/get_properties` (as a single object), and embedded
in `participant_create` / `participant_update` SSE events. **Same shape in
all three.**

```jsonc
{
  // Identity
  "uuid":                       "<participant-uuid>",
  "uri":                        "alice@example.com",   // empty string for guests
  "vendor":                     "Pexip Infinity Client", // user-agent / endpoint vendor; "" for guests
  "display_name":               "Alice",
  "overlay_text":               "Alice (Sales)",        // currently rendered overlay
  "local_alias":                "meet.alice",           // the alias this participant joined via
  "external_node_uuid":         "<uuid>",

  // Role / status
  "role":                       "chair" | "guest",      // note: lowercase, unlike request_token's HOST/GUEST
  "service_type":               "conference" | "lecture" | "gateway" | "test_call"
                                | "waiting_room" | "ivr" | "connecting",
  "protocol":                   "api" | "webrtc" | "sip" | "rtmp" | "h323" | "teams" | "mssip",
  "call_direction":             "in" | "out",
  "start_time":                 1715800000,
  "call_tag":                   "ops-bot-7",            // echoed back from request_token

  // Audio / video state
  "is_muted":                   "YES" | "NO",           // server-side mute (audio path blocked at the mixer)
  "is_video_muted":             true,                   // server-side video mute (boolean!)
  "is_client_muted":            false,                  // local "I appear muted in UI" only (cosmetic)
  "is_tx_muted":                false,
  "is_video_silent":            false,                  // server-side detected silent video
  "is_main_video_dropped_out":  false,                  // not in the main mix right now (e.g. AC dropped silent)
  "is_audio_only_call":         "YES" | "NO",
  "is_video_call":              "YES" | "NO",

  // Presentation
  "is_presenting":              "YES" | "NO",
  "presentation_supported":     "YES" | "NO",
  "rx_presentation_policy":     "ALLOW" | "DENY",
  "needs_presentation_in_mix":  false,

  // Capabilities (server's view of what the client can do)
  "disconnect_supported":       "YES" | "NO",
  "mute_supported":             "YES" | "NO",
  "transfer_supported":         "YES" | "NO",
  "fecc_supported":             "YES" | "NO",
  "supports_direct_chat":       false,
  "can_receive_personal_mix":   true,

  // Engagement
  "buzz_time":                  0,                       // unix ts of last raised hand, 0 if not raised
  "spotlight":                  0,                       // unix ts when spotlight was set, 0 if off
  "last_spoken_time":           1715800012.234,          // float seconds
  "show_live_captions":         false,

  // Mixing / layout
  "layout_group":               "a",                     // for pinning
  "send_to_audio_mixes":        [ { "mix_name": "main", "prominent": false } ],
  "receive_from_audio_mix":     "main",
  "encryption":                 "On" | "Off",

  // Auth / IDP
  "is_idp_authenticated":       false,

  // State flags
  "is_external":                false,
  "is_conjoined":               false,
  "is_on_hold":                 false,
  "is_streaming_conference":    false,
  "is_transferring":            false,
  "has_media":                  true,                    // false for api-only participants

  // Custom data
  "custom_properties":          null,                    // dict | null
  "private_custom_properties":  null                     // dict | null (only sent to host viewing this participant)
}
```

Trivia that bites:

- **`role` is lowercase** (`chair` / `guest`) here, vs uppercase
  (`HOST` / `GUEST`) in `request_token`. They mean the same thing.
- **YES/NO strings vs booleans** — several fields are stringly-typed
  (`is_muted`, `is_video_call`, `disconnect_supported`, etc.) while others
  are real booleans (`is_video_muted`, `is_client_muted`,
  `is_main_video_dropped_out`). Treat the strings as canonical and parse to
  bool in your model layer.
- **`overlay_text` vs `display_name`** — display_name is the participant's
  reported name; overlay_text is what's currently rendered on the stage. A
  host calling `overlaytext` mutates `overlay_text`, never `display_name`.

---

## Per-participant control endpoints

All are `POST`. Default body is `{}` unless specified.

### Audio / video mute

| Endpoint | Effect |
|---|---|
| `mute` | Server-side audio mute (mixer blocks the audio). Host-only on others; self-mute also works. |
| `unmute` | Inverse. Subject to `guests_can_unmute` if you're a guest. |
| `video_muted` | Server-side video mute. |
| `video_unmuted` | Inverse. |
| `client_mute` | Cosmetic — flips the "appears muted in UI" indicator. Doesn't actually block audio. Use case: clients that handle audio gating locally. |
| `client_unmute` | Inverse. |

### Layout / display

| Endpoint | Body | Effect |
|---|---|---|
| `spotlighton` | `{}` | Pin this participant to the main stage. |
| `spotlightoff` | `{}` | Unpin. |
| `overlaytext` | `{ "text": "VIP Guest" }` | Override the participant's overlay name (host-only). |
| `layout_group` | `{ "layout_group": "a" }` | Assign to a pinning layout group. |
| `preferred_aspect_ratio` | `{ "aspect_ratio": 1.78 }` | Hint the receive aspect ratio. |
| `pres_in_mix` | `{ "setting": true }` | (AC layouts only) include this participant's presentation in the main mix. |
| `send_to_audio_mixes` | `{ "mix_name": "main", "prominent": false }` (per mix, list) | Which audio mixes the participant sends to. |
| `receive_from_audio_mix` | `{ "mix_name": "main" }` | Which mix the participant receives. |

### Hand / floor / spotlight

| Endpoint | Effect |
|---|---|
| `buzz` | Raises this participant's hand (sets `buzz_time` to now). |
| `clearbuzz` | Lowers their hand. |
| `take_floor` | Start full-motion presentation. Pair with `release_floor` when done. |
| `release_floor` | End presentation. |
| `allowrxpresentation` | Allow this participant to receive presentation. |
| `denyrxpresentation` | Block their presentation receive. |

### Captions

| Endpoint | Effect |
|---|---|
| `show_live_captions` | Enable live captions for this participant; arrives as `live_captions` SSE events on their stream. |
| `hide_live_captions` | Disable. |

### Disconnect / transfer / role

| Endpoint | Body | Effect |
|---|---|---|
| `disconnect` | `{}` | Kick this participant. |
| `unlock` | `{}` | Admit from waiting room (host-only). |
| `role` | `{ "role": "chair" \| "guest" }` | Promote/demote (host-only). |
| `transfer` | `{ "conference_alias":"<alias>","role":"guest" \| "host","pin":"1234" }` | Move them to another conference. |

### DTMF / FECC / messaging

| Endpoint | Body | Effect / when usable |
|---|---|---|
| `dtmf` | `{ "digits": "1234#" }` | Send DTMF tones to *this participant* (gateway calls — to drive an IVR they're attached to). |
| `fecc` | (see `calls-media.md`) | Far End Camera Control — gateway only. Requires `fecc_supported: true`. |
| `message` | `{ "type":"text/plain","payload":"hi" }` | Direct message to one participant. They receive a `message_received` SSE event with `direct: true`. |

### Properties / stats / attestation

| Endpoint | Effect |
|---|---|
| `GET get_properties` | Full participant object (see §"The participant object"). |
| `GET avatar.jpg` | Avatar image (set by External Policy's participant-avatar response, or by IDP). 404 if none. |
| `GET get_attestation` | Returns a JWT asserting the participant's role/identity. Useful for downstream services verifying who the participant is. JWT body: `{ role, conf, exp, kid }`. Verify via the node's `/api/client/v2/jwk` endpoint. |
| `POST statistics` | Report media stats — direct-media only. Body: `{audio:{…},video:{…},presentation:{…}}` (see `calls-media.md` for the full shape). |

---

## Self vs other action matrix

| Action | On self | On others |
|---|---|---|
| `mute` / `unmute` | Always (subject to guest-unmute config) | Host only |
| `video_muted` / `video_unmuted` | Always | Host only |
| `client_mute` / `client_unmute` | Always | Rarely useful for others |
| `take_floor` / `release_floor` | Always (subject to presentation policy) | Host only |
| `spotlighton` / `spotlightoff` | n/a (you don't spotlight yourself) | Host only |
| `disconnect` | Always (you can drop yourself; same as `release_token`) | Host only |
| `role` change | No (can't self-promote) | Host only |
| `transfer` | No (use `refer` event + new `request_token`) | Host only |
| `buzz` | Yes (raise hand) | Host only (raise someone else's hand — unusual) |
| `clearbuzz` | Yes (lower own) | Host only |
| `dtmf`, `fecc` | Always (sending toward your own call) | Host only |
| `overlaytext` | No | Host only |
| `show_live_captions` | Yes (for self) | Host only |
| `message` (direct) | n/a (you'd be messaging yourself) | Any, to any |
| `get_properties`, `avatar.jpg`, `get_attestation` | Yes | Yes (any participant) |

A guest token's failed write tends to return
`{"status":"failure","result":"…"}` with no machine-readable error code. In
your client, branch on `role` from `request_token` rather than firing
host-only writes speculatively.
