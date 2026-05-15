# WebRTC failure patterns

What to look for when the failing leg is WebRTC — browser or Pexip Webapp
client connecting to a Conferencing Node over the Pexip client v2 REST API
plus a peer-to-peer media path.

WebRTC traces live in `support_log/` across these components:

- `support.rest` — token request, candidate trickle, mute, disconnect
- `support.ice` — local/remote candidate events, selected pair
- `support.crypto.keys` — DTLS-SRTP keying
- `support.media` — codec/resolution activation
- `support.participant` — stream lifecycle + RX/TX stats on teardown

There is **no SIP-style response code** for WebRTC failure. Instead,
failure presents as a phase of the state machine that never completes.

---

## The healthy WebRTC sequence

```
1. Client → POST  /api/client/v2/conferences/<vmr>/request_token
   Response: token, role, conference settings, feature flags
2. Client → POST  …/calls           (with SDP offer)
   Response: SDP answer + call_uuid
3. ICE gathering (parallel to step 2):
     Conferencing Node emits multiple support.ice "new-local-candidate"
     Client trickles candidates via …/<call_uuid>/new_candidate
4. ICE connectivity checks resolve → support.ice "new-selected-pair" per component
5. DTLS handshake completes → support.crypto.keys "New encryption suite" (one for encryption, one for decryption)
6. Media activation → support.media "New mode activated" per stream
7. Second "Participant has joined" with Protocol="WebRTC"
8. Mid-call: REST API calls for mute/unmute, layout, presentation
9. Teardown: support.participant "Media Stream destroyed" with stats,
   then administrator.conference "Participant has disconnected" with Duration
```

If a call stops between steps 3 and 5, it is **almost always** an ICE/NAT
or DTLS issue. Steps 5→6 failing usually means SRTP profile or codec.
Step 8 failures are media-quality, not connection.

---

## ICE phase failures

### Symptom A — ICE gathering succeeds, no candidates from client

Log signature:

```
support.ice "ICE new-local-candidate event"   (many lines, server side)
support.rest …/new_candidate                  (zero or one)
```

Diagnosis: client never trickled candidates. Most often:

- Client-side ICE gathering blocked by browser permissions or by an
  `enterprise policy` disabling WebRTC.
- Client is behind symmetric NAT and the response to STUN was filtered;
  client has no STUN/TURN configured.
- `request_token` response had empty `"turn": []` — Pexip didn't issue
  TURN credentials. Check whether **TURN server** is configured at
  `Platform > Locations > TURN server`.

### Symptom B — Candidates exchanged, no selected pair

Log signature:

```
support.ice "ICE new-local-candidate event"   (multiple, server)
support.ice "ICE setting remote candidate"    (multiple, client)
support.ice "ICE new-selected-pair event"     (MISSING)
```

After ~30 s the call dies. This is **the classic NAT traversal failure**.
Causes ordered by likelihood:

1. **No common reachable transport.** Both endpoints offered only host
   candidates; their networks can't reach each other directly. Need
   srflx (STUN) or relay (TURN) candidates. Look at the `Local-Candidate-Type`
   distribution — are there any `srflx` or `relay`? If everything is `host`,
   that's the problem.
2. **Firewall blocking UDP**. Even with srflx candidates, the connectivity
   checks themselves get dropped. TCP fallback (`Local-Candidate-Transport="tcp-pass"`
   / `"tcp-act"`) exists but is slow and sometimes blocked too. Check
   whether any candidate pair makes it to "checking" state in
   developer_log.
3. **TURN unreachable.** Pexip issued a TURN credential but the client
   can't reach the TURN host on UDP/3478 or TCP/443. Common with
   enterprise proxies that don't allow non-HTTP CONNECT.
4. **Trickle ICE disabled or stalled.** Some browsers / Pexip versions
   disable trickle; ICE must wait for the full candidate set. If
   `"trickle_ice_enabled": false` in the token response and the client
   sent its SDP before gathering finished, the answer has no usable
   candidates.

### Symptom C — Selected pair, then media stops

Log signature:

```
support.ice "ICE new-selected-pair event"     ← present
support.crypto.keys "New encryption suite"    ← present
support.media "New mode activated"            ← present (briefly)
… (silence) …
support.participant "Media Stream destroyed"  with RX rate dropping to 0 / high loss
```

This is **mid-call connectivity loss**. Look at the RX/TX stats embedded
in the `Media Stream destroyed` Detail field:

- `loss 0%` with `RX rate` collapsing → network path failed silently
  (no RTCP NACK loop, just no packets).
- `loss > 5%` with rising jitter → quality, not connectivity. See "Media
  quality" below.

ICE restart (mobility) usually rescues this — failure to restart suggests
the client lost the WebSocket signalling channel too.

---

## DTLS phase failures

Log signature:

```
support.ice "ICE new-selected-pair event"     ← present
support.crypto.keys "New encryption suite"    ← MISSING
```

Causes:

1. **Certificate fingerprint mismatch.** The `a=fingerprint:` in the SDP
   doesn't match the DTLS handshake cert. Often happens when an SBC or
   media-relay rewrote the SDP without updating the fingerprint. Look
   for `support.dtls "handshake failed" Reason="bad_certificate"` in
   developer_log.
2. **DTLS role mismatch (`setup:`).** Both sides claim `actpass`, or both
   claim `active`. Standard says exactly one must be `active` for the
   handshake to proceed. Check the offer/answer pair in the
   `…/calls` request and response — Pexip should answer `setup:active`
   to a client `setup:actpass`.
3. **DTLS over TCP being blocked.** If ICE selected a TCP candidate pair
   and the firewall does deep packet inspection that blocks DTLS, the
   handshake silently fails. Switch back to UDP if possible.

---

## STUN / TURN failures

STUN is usually invisible — successful binding requests don't log. You
notice failure by **absence of srflx candidates** in `support.ice
"new-local-candidate"` lines.

For TURN, look for:

- `request_token` response `"turn"` field — empty array means Pexip didn't
  issue credentials.
- Pexip's external TURN server (`mtls`-protected or shared-secret) logs
  separately; they're not in the support snapshot. If TURN credentials
  were issued but no relay candidate appears, the TURN host is
  unreachable from the client.

A useful diagnostic when TURN is suspect: have the user run
`https://webrtc.github.io/samples/src/content/peerconnection/trickle-ice/`
in their browser with the same TURN credentials and confirm relay
candidates appear.

---

## Codec / media negotiation failures

Log signature:

```
support.crypto.keys "New encryption suite"   ← present
support.media "New mode activated"           ← MISSING for one or more streams
```

Diagnosis: DTLS is up, but no codec was agreed for a stream. Compare
the `m=audio` / `m=video` payload type lists in the offer (client) and
answer (Pexip):

- Pexip's answer is in the `…/calls` REST response Detail. Look for
  `m=audio … 111 9 0 8 126 110` style lines.
- Client offer is in the same call's REST **request** Detail.
- If the answer has fewer or different payload types than the offer,
  one side rejected codecs. Pexip will downgrade gracefully to PCMU
  for audio; if even PCMU isn't in the offer, audio fails.
- For video, VP8 is the safest fallback. H.264 may fail on platforms
  without hardware decoders.
- **AV1 and H.265** are often offered but not actually decodable —
  check whether the agreed codec is one of these and the call dies
  immediately after media starts.

The `support.media "New mode activated"` line contains the chosen mode,
e.g. `Mode="VP9 [720p(1280x720)@30fps (1200000bps)] pt:98 ssrc:0"`. If
the mode is missing entirely, the stream never started.

---

## WebSocket / signalling channel failures

The Pexip Webapp can use a WebSocket (`wss://`) for the events stream in
addition to the REST polling. Failure looks like:

- `Name="connectivity"` lines for `wss://` upgrade returning 4xx (often
  401 — token expired) or never responding (proxy / firewall).
- Mid-call, the WebSocket disconnects → client falls back to long-polling
  → events arrive late or out of order → the user sees "frozen" UI even
  though media is fine.

In the snapshot, look at `support.rest` lines around the failure window:
gaps > 30 s between requests for the same Uuid suggest the events channel
died.

---

## Browser / client-side issues that look like Pexip failures

Some failure modes are entirely client-side but surface in Pexip logs as
unusual sequences:

- **Browser ran out of media slots.** Chrome enforces a maximum number of
  active `RTCPeerConnection`s. The token request succeeds, the calls
  request succeeds, then ICE never starts because the client peerConnection
  is in a bad state.
- **HTTPS certificate not trusted.** The token request fails entirely —
  no Pexip log at all because the request never reached the node. Confirm
  by asking the user to load the Webapp in the browser and check for cert
  warnings.
- **Camera/mic permission revoked.** ICE and DTLS succeed, but the
  outbound media (TX) is silent and the inbound media is fine. RX/TX
  stats on disconnect show `TX rate 0`.

---

## Quality (loss, jitter, MOS)

For a quality-not-connectivity report:

- `support.participant "Media Stream destroyed"` Detail field has compact
  per-stream stats:

  ```
  Stream 1 (video)
    RX: rate 1466kbps loss 0.00% jitter 0ms
        codec H264_B_0 resolution 1280x720 fps 30
    TX: rate 656kbps loss 0.00% jitter 11ms
        codec VP9 rate 656kbps resolution 1280x720 fps 30
  ```

- For mid-call quality, Pexip emits periodic `support.media` updates
  with the active mode. Repeated downshifts (`VP9 720p` → `VP9 360p`
  → `VP9 180p` in <60 s) indicate bandwidth pressure.
- High jitter (>30 ms) typically means packet reordering or a saturated
  uplink.
- Loss >2 % is noticeable; >5 % degrades audio meaningfully.
- Pexip's adaptive bitrate will downshift in response — that's a
  symptom, not a cause.

MOS scores aren't directly logged in support snapshots; they're computed
in the analytics database. If the user has access to the
**Conferencing Node > Status > Statistics** page they can see live MOS.
