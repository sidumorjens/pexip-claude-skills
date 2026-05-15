# Calls & WebRTC Media — Reference

Pexip's Client API doesn't speak SIP, H.323, or any media-plane protocol
directly to the client. Instead, it carries SDP and ICE candidates **inside
REST calls** (`/calls/…`) and **inside SSE events** (`new_offer`,
`new_candidate`, `update_sdp`). Your WebRTC stack does the media; the
REST/SSE channel is the signalling.

This reference covers both modes — **transcoded** (Pexip mixes the media
centrally) and **direct-media** (peers exchange media end-to-end, with
Pexip only relaying ICE/SDP). They differ in flow ordering and in which
SSE events you must handle.

---

## The endpoints

All under `/api/client/v2/conferences/<alias>/participants/<participant_uuid>/`:

| Endpoint | Purpose |
|---|---|
| `POST calls` | Open a call. Body carries the local SDP; response carries the remote SDP (or empty, for direct media). |
| `POST calls/<call_uuid>/ack` | Tell Pexip media is ready; start RTP. |
| `POST calls/<call_uuid>/new_candidate` | Send a local ICE candidate (trickle ICE). |
| `POST calls/<call_uuid>/update` | Renegotiate SDP (ICE restart, codec change, TCP fallback). |
| `POST calls/<call_uuid>/disconnect` | Hang up this call. |
| `POST calls/<call_uuid>/dtmf` | DTMF digits (gateway calls only). |
| `POST calls/<call_uuid>/fecc` | Far End Camera Control (gateway calls only, FECC-capable endpoints only). |
| `POST statistics` | (Participant-level, not call-level.) Report media stats — direct-media only. |

---

## `POST /participants/<uuid>/calls` — open a call

### Request body

```jsonc
{
  "call_type":       "WEBRTC",          // currently the only supported value
  "sdp":             "<local SDP offer>",
  "media_type":      "video",           // "video" (audio+video+presentation),
                                        // "video-only" (audio+video),
                                        // "audio" (audio only)
  "fecc_supported":  false,
  "present":         "main"             // optional: receive presentation IN PLACE OF main video
                                        // (single-stream client)
}
```

- `media_type` determines how many m-lines you should put in your SDP:
  - `"audio"` → 1 m-line (audio).
  - `"video-only"` → 2 m-lines (audio + video).
  - `"video"` → 3 m-lines (audio + video + presentation).
- `"present": "main"` lets a single-stream client receive presentation by
  swapping it for main video on the existing video stream. Don't combine
  with a 3rd m-line for presentation.
- `fecc_supported: true` declares your client can receive FECC requests
  *from* the far end (typically gateway endpoints). To actually send FECC,
  see `/fecc` below.

### Response

```jsonc
{
  "status": "success",
  "result": {
    "call_uuid":  "<call-uuid>",
    "sdp":        "<remote SDP answer>",   // may be "" in direct-media mode (see below)
    "turn":       [ { "urls": [...], "username":"…", "credential":"…" } ]
  }
}
```

- `call_uuid` identifies this call for all subsequent endpoints.
- `sdp` is the remote answer. In **transcoded** mode you get it
  immediately; in **direct-media** mode it may be empty (means "far end
  isn't ready yet — wait for the `new_offer` event").
- `turn` may include additional TURN servers (e.g. TCP/443 fallback if your
  deployment runs it). Add them to your ICE configuration.

---

## Transcoded mode — the simple flow

1. Build your local SDP offer (audio + video + maybe presentation).
2. `POST /calls` with the offer.
3. Receive Pexip's SDP answer immediately.
4. ICE: gather local candidates, send each via `POST /new_candidate`. Pexip's
   candidates are baked into its SDP (no trickle from Pexip → you).
5. When ICE is complete and media is set up, `POST /ack` to start RTP.
6. Media flows through the conferencing node (it composes the mix).

There is **no `new_offer` / `update_sdp` / `peer_disconnect`** flow in
transcoded mode — Pexip is the single remote.

State machine summary:

```
[idle] --POST calls--> [offer-sent]
                          |
                          v
                  (SDP answer received)
                          |
                          v
                  [ICE in progress] --POST new_candidate (local)--> [ICE in progress]
                          |
                          v
                  (ICE selected pair found)
                          |
                          v
                          --POST ack--> [media flowing]
                          |
                          v
                          --POST disconnect--> [done]
```

---

## Direct-media mode — the reactive flow

The Conferencing Node is **not** the remote endpoint here — another
participant is. The node only relays signalling. Your `request_token`
response tells you you're in this mode:

```json
{ "direct_media": true,
  "pex_datachannel_id": "42",
  "client_stats_update_interval": "1000",
  "use_relay_candidates_only": false,
  "stun": [...], "turn": [...] }
```

### Joining first (no peer yet)

1. `POST /calls` with your local offer SDP.
2. Response `sdp` is **empty** — that's normal, far end not ready.
3. **Do not call `/ack` yet.** Don't time out aggressively.
4. Wait for the SSE `new_offer` event:
   ```json
   { "sdp": "<remote offer>" }
   ```
5. Apply the remote SDP, generate your answer, `POST /ack` with the answer
   in the body:
   ```json
   { "sdp": "<your answer>" }
   ```
6. ICE: send local candidates via `POST /new_candidate`, receive remote
   candidates via SSE `new_candidate` events.
7. Media flows peer-to-peer.

### Joining when a peer is already present

Same as above, but step 2's response usually carries the remote SDP
directly — you can `POST /ack` immediately and `new_offer` won't fire.

### Mid-call renegotiation

The remote can re-offer at any time (e.g. ICE restart, network change):

- SSE `update_sdp` event arrives with new remote SDP.
- Apply it, generate a new answer, `POST /update` with the answer:
  ```json
  { "sdp": "<your new answer>", "fecc_supported": false }
  ```

### Peer leaving

- SSE `peer_disconnect` event arrives.
- Your call is still alive (Pexip will refresh the negotiation when a new
  peer joins). Display "waiting for participants" / show splash screen.

### State machine summary

```
[idle] --POST calls--> [offer-sent]
                          |
              (response.sdp empty)        (response.sdp non-empty)
                          |                       |
                          v                       v
              [waiting new_offer]          [answer-received]
                          |                       |
              (new_offer event arrives) |
                          v                       |
                          v                       v
                  Generate answer
                          |
                          v
                          --POST ack with {sdp: answer}--> [media flowing]
                          |   ^
                          |   |  (update_sdp event → POST /update — loop)
                          v   |
                          --POST disconnect--> [done]
```

ICE trickle is **bidirectional** in direct media: send via `POST /new_candidate`,
receive via SSE `new_candidate`. Apply remote candidates to your peer
connection as you receive them. The candidate format on the wire:

```json
{
  "candidate": "candidate:1732786348 1 udp 2124262783 2a02:c7f:615… ufrag YAeD network-id 2 network-cost 10",
  "mid":       "0",
  "ufrag":     "YAeD",
  "pwd":       "IfZniTlYHipJXEg4quoI00ek"
}
```

`mid` is the SDP m-line identifier (`a=mid:0`); pass through to your
WebRTC API's `addIceCandidate`.

---

## Presentation (screenshare)

### Sending

Your initial `/calls` SDP must include a 3rd m-line marked as presentation
content:

```
m=application 9 UDP/TLS/RTP/SAVPF 100
a=mid:2
a=content:slides
…
```

(WebRTC stacks generally call this a "secondary video" track with the
`content:slides` attribute. The mechanics vary by library; Pexip cares
about the `a=content:slides` line specifically.)

To start presenting:

```
POST /participants/<uuid>/take_floor
```

When done:

```
POST /participants/<uuid>/release_floor
```

Pexip emits `presentation_start` / `presentation_stop` to all participants.

### Receiving

Two modes:

- **Separate stream**: include a 3rd m-line in your `/calls` offer.
  Receive presentation as a distinct video track. Higher bandwidth, richer
  UX (see slides + faces side-by-side).
- **In place of main**: set `"present": "main"` in your `/calls` request.
  Pexip swaps the presentation into the main video stream when someone
  presents. Lower bandwidth, simpler client.

Presentation **state changes** arrive as SSE events:

- `presentation_start` — `{"presenter_name":"…","presenter_uri":"…","source":"video"|"static"}`.
- `presentation_stop` — empty.

### Presentation snapshots (frames)

For control clients or recorders that don't process the media but want a
visual record of the presentation, Pexip serves JPEG snapshots:

```
GET /api/client/v2/conferences/<alias>/presentation.jpeg?token=<token>
GET /api/client/v2/conferences/<alias>/presentation_high.jpeg?token=<token>
```

A `presentation_frame` SSE event fires whenever a new frame is available —
treat it as a polling trigger, not a payload. (The frame itself is the
JPEG you fetch.)

> ⚠️ Frame URLs may also accept a `id=<event_id>` query parameter when one
> is provided in the SSE. Behaviour varies by version.

---

## FECC (Far End Camera Control)

Only meaningful for gateway calls to FECC-capable endpoints (typically SIP
or H.323 hardware). Body shape:

```jsonc
{
  "action":   "start" | "continue" | "stop",
  "movement": [
    { "axis": "pan"  | "tilt" | "zoom",
      "direction": "left" | "right" | "up" | "down" | "in" | "out" }
  ],
  "timeout":  1000     // ms — typically 1000 for start, 200 for continue
}
```

Pattern: start with `action: "start"` (movement specified, timeout 1000ms);
while the user holds the button, every ~200ms send `action: "continue"`
with the same movement and timeout 200; on release send `action: "stop"`
with movement specified one last time.

You must have set `fecc_supported: true` in `/calls` (or `/update`) for
this to work.

---

## DTMF

`POST /participants/<uuid>/calls/<call_uuid>/dtmf`:

```json
{ "digits": "1234#" }
```

Gateway calls only — for in-band signalling to PSTN/SIP IVRs. The
participant-level `POST /participants/<uuid>/dtmf` (same body) is functionally
the same and is usually easier to call (no `call_uuid` required).

---

## Statistics — direct media only

In direct-media mode, the conferencing node can't see the media, so the
client reports stats explicitly:

```
POST /participants/<participant_uuid>/statistics
```

Body — every interval (`client_stats_update_interval` from `request_token`):

```jsonc
{
  "audio": {
    "rx_bitrate":          64.4,
    "rx_codec":            "opus",
    "rx_jitter":           2,
    "rx_packets_lost":     0,
    "rx_packets_received": 914,
    "tx_bitrate":          63.728,
    "tx_codec":            "opus",
    "tx_packets_sent":     914,
    "tx_rb_jitter":        2,
    "tx_rb_packetslost":   0
  },
  "video": {
    "rx_bitrate":          2215.744,
    "rx_codec":            "VP8",
    "rx_fps":              21,
    "rx_packets_lost":     0,
    "rx_packets_received": 4206,
    "rx_resolution":       "1280x720",
    "tx_bitrate":          2089.296,
    "tx_codec":            "VP8",
    "tx_packets_sent":     3633,
    "tx_rb_packetslost":   0,
    "tx_resolution":       "1280x720"
  },
  "presentation": {
    "rx_packets_lost":     0,
    "rx_packets_received": 0,
    "tx_bitrate":          989.304,
    "tx_codec":            "VP8",
    "tx_packets_sent":     1714,
    "tx_rb_packetslost":   0,
    "tx_resolution":       "1792x1120"
  }
}
```

Fields are optional — omit sections (or their inner fields) you don't
have. In transcoded mode, **do not** call this endpoint; Pexip ignores it
and the data isn't used.

---

## Common pitfalls

1. **An empty SDP answer is not an error.** In direct-media mode it means
   "wait for `new_offer`". Code that times out at 5s here breaks for the
   first joiner to a room.

2. **`/ack` is the *start media* signal**, not an HTTP acknowledgement.
   Missing it leaves the call set up but silent — the call appears
   connected in `/participants` but no RTP flows.

3. **Track `call_uuid` per call, not per participant.** A participant can
   have multiple calls (main media call + presentation call). Each gets
   its own UUID; renegotiation is per-call.

4. **`new_candidate` events apply to a specific call.** The event payload
   doesn't include `call_uuid`. With one media call per participant this
   is unambiguous; with multiple calls you'll need to track the active
   one and rely on `mid` to disambiguate media line.

5. **Disconnect cleanup.** `POST /calls/<uuid>/disconnect` ends *the
   call*. To also leave the conference, follow with `POST /release_token`.
   In the other direction, `release_token` implicitly disconnects all
   calls.

6. **`use_relay_candidates_only`** is Pexip telling you to disable host /
   srflx candidates and only use the TURN-relayed ones. Honour it —
   ignoring this in restrictive networks breaks media.

7. **Presentation as separate stream vs `present: "main"`** is decided at
   call setup, not at `take_floor` time. Plan up front.

8. **VP9 / 1080p / FECC capability is double-gated.** `request_token`'s
   `vp9_enabled` / `allow_1080p` / `fecc_enabled` tells you what the
   *conference* allows. Whether *your call* uses them depends on your SDP
   offer and `fecc_supported` flag. Negotiate generously, drop gracefully.
