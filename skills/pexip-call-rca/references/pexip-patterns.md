# Pexip-specific patterns

Pexip Infinity emits a number of platform-level messages whose root cause
isn't obviously a SIP or WebRTC failure — they're Pexip itself refusing,
running out of resources, or routing the call somewhere bad. This file
covers the high-signal ones.

---

## License limits

| Message | Diagnosis |
|---|---|
| `Message="License limit reached"` / `Reason="port_limit_reached"` | Concurrent **port licenses** (audio+video participants) exhausted. New joins fail; existing calls continue. |
| `Reason="vmr_limit_reached"` | VMR-license tier exceeded; not all Pexip versions. |
| `Reason="registration_limit_reached"` | Registered-endpoint license exhausted. SIP/H.323 device registrations fail. |

Verify via **Administration > Status > Licenses**. Port licenses are
node-pool-wide, not per-node — capacity issues on one location can be
solved by routing calls to another.

Notably: `Licenses="0"` on a *participant join* line is **not** a failure
— it's the API leg (no media), which doesn't consume a port. The
follow-up media-leg join shows `Licenses="1"`.

---

## Locked VMR / authentication

| Message | Diagnosis |
|---|---|
| `Service-Tag="locked"` in admin lines | Informational — the VMR is configured with a host PIN, doesn't mean entry failed. |
| `Message="PIN entry incorrect."` | Wrong PIN. Repeated attempts: brute force or wrong-PIN-config. |
| `Message="Authentication failed."` Reason="…" | Either the conference PIN is wrong, or the participant tried to enter a guest PIN where only host is allowed, or vice versa. The `Role="host\|guest"` field tells you which role was attempted. |
| `Message="Conference locked"` / `Detail="conference_locked"` | Host explicitly locked the meeting after start; new participants rejected. Not a system fault. |
| `Message="Participant rejected"` Reason="host_not_present" | "Wait for host" policy active, no host has arrived. |

For SAML/OIDC SSO joins, look at the `IDP-Authenticated="False"` field on
the join attempt: `True` means a valid IDP token was presented; `False`
on a VMR that requires IDP-auth means the user attempted to bypass.

---

## Capacity / placement failures

| Message | Diagnosis |
|---|---|
| `Message="No available media nodes"` / `Reason="no_capacity"` | Media resources exhausted at the chosen Location. May also mean **every conferencing node in the location is at max calls** even if licenses are free (CPU limit). |
| `Message="Media node unreachable"` | Signaling node accepted the call but the chosen media node didn't respond. Likely network issue between signaling and media nodes (cross-location bridge link, firewall). |
| `Reason="placement_failed"` | The Pexip "placement" algorithm couldn't pick a media node satisfying constraints (location, codec, capacity). Check `Media routing` rules and Location bandwidth limits. |
| `Message="Connectivity test failed"` between nodes | Edge ↔ Transcoding split: Edge node can't reach the Transcoding node it tried to hand the call to. Look at `connectivity` log component. |

When the snapshot includes `system_metrics/`, check CPU on each
conferencing node around the failure timestamp — a node with 100 % CPU
will fail placement even with licenses available.

---

## Routing failures

| Message | Diagnosis |
|---|---|
| `Message="Call routing rule did not match"` | Dialed alias didn't match any configured **Call routing rule**. The participant sees "Conference not found" or equivalent. Check rules under **Service configuration > Call routing rules**. |
| `Message="Conference not found"` `Alias="..."` | The alias matched a routing rule but the destination VMR/service doesn't exist or is disabled. |
| `Message="Service disabled"` | The VMR or virtual reception is provisioned but `Enabled` is unchecked. |

When troubleshooting routing, dump `administrator_log` for
`Message="Call routing rule did not match"` and check whether the
**Match** pattern column is what you expect. Pexip's routing rules are
ordered and first-match-wins.

---

## BFCP / content sharing

BFCP (Binary Floor Control Protocol) coordinates presentation/content
streams on SIP/H.323. Failures:

| Pattern | Diagnosis |
|---|---|
| BFCP `FloorRequest` → no `FloorGranted` | Far-end doesn't have a free floor. Either someone else is already presenting and the conference is in "one presenter" mode, or BFCP is disabled in the VMR. |
| BFCP transport mismatch | UDP vs TCP — Pexip negotiates per-call but some SBCs strip the `a=floorctrl:` line. SDP rewrite issue. |
| Presentation stream `a=inactive` on both sides | Normal when nobody is sharing — not a failure. |

For WebRTC, presentation uses an additional `m=video` section labeled
`content:slides`. Failure to start sharing is usually a screen-capture
permission issue on the client, not a Pexip issue.

---

## Gateway calls (SIP ↔ WebRTC, SIP ↔ H.323)

A Pexip "gateway call" is when one participant joins via SIP and Pexip
internally bridges them into a VMR or directly to another participant.
The call has two legs from Pexip's perspective:

- The **inbound leg** (e.g. SIP INVITE from an SBC)
- The **outbound leg** (e.g. an internal call into the WebRTC mix)

Failures specific to gateways:

| Pattern | Diagnosis |
|---|---|
| Inbound SIP succeeds, outbound leg never starts | Pexip's `Call routing rule` mapped to a destination that doesn't exist, or the destination requires features the inbound leg doesn't have (e.g. H.265 only). |
| Inbound leg shows `488 Not Acceptable` after Pexip's answer | Outbound leg negotiated codecs that the inbound peer can't transcode to. Check the **Transcoding node** location and ensure media-transcoding licenses. |
| BFCP works on the SIP side, doesn't propagate to WebRTC | BFCP-to-content-share bridge requires the VMR to have `Allow content sharing` enabled. |
| H.323 inbound, WebRTC outbound, audio works, video doesn't | H.264 profile mismatch. Pexip may have answered with `profile-level-id=42c014` but the H.323 endpoint only supports `42801F`. |

Gateway calls produce two `Conference-ID`s in some Pexip versions
(internal pseudo-conference for the bridge). Correlate the legs by
`Call-Id` chain — Pexip logs both sides' `Call-Id` on the bridge event.

---

## Direct media

When the VMR has `Direct media` enabled (peer-to-peer when only two
participants), the second participant's media path is **direct between
clients**, not through Pexip. Symptoms:

| Pattern | Diagnosis |
|---|---|
| `"direct_media": true` in the token response | The call may go direct. |
| Only the first participant has `Media-Node="…"` set; the second has it empty | Direct media is active for the second. Their media path **never appears in Pexip logs**. If they report a media problem, the snapshot won't show it. |
| Direct media call escalates to 3+ participants | Pexip transparently re-routes through a media node; expect a brief media glitch as ICE renegotiates. |

If the user reports a media issue and direct media was active for the
affected participant, you need their client's `chrome://webrtc-internals`
dump, not the Pexip log.

---

## Mute / unmute / API mid-call

Mid-call API mutes and unmutes are normal noise:

```
REST POST  …/client_unmute       → 200
admin event "Participant client unmute requested by API."
```

The interesting variant:

| Message | Diagnosis |
|---|---|
| `Message="Mute denied"` / `Reason="server_muted"` | The host muted the participant; participant tried to self-unmute, was denied. Behaviour, not a failure. |
| `Message="Participant client unmute requested by API."` paired with `Detail="Server muted"` | Same as above. |
| Repeated `client_unmute` then `client_mute` cycling | UI / browser bug on the client. Pexip logs the requests but they're not breaking anything. |

---

## Disconnect reasons

The `Detail` field on `Participant has disconnected` carries a
human-readable reason. The common values:

| Detail | Meaning |
|---|---|
| `User initiated disconnect` | Participant clicked Leave / hung up. |
| `Call disconnected` | Generic — usually the API leg counterpart to a WebRTC media disconnect. |
| `Conference ended` | Host ended the meeting; everyone disconnected as a result. |
| `Removed from conference` | A host kicked the participant. |
| `Call timed out` | Pexip detected no media for the configured idle timeout (default 60 s). Connectivity loss. |
| `Conference duration exceeded` | VMR's max duration reached. |
| `Backend error` | Internal Pexip error — open a support case. |
| `License unavailable` | Mid-call license loss (rare; usually only on join). |
| `Authentication failed` / `Wrong PIN` | Joined-but-got-kicked-out flows. |
| `Encrypted media not negotiated` | The peer's SDP didn't include a viable media-encryption profile and the VMR requires it. |

Always quote the **exact** Detail value when citing a disconnect reason
in the RCA — there is no fuzzy matching; "Call disconnected" and "Call
timed out" mean very different things.
