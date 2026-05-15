# SIP failure patterns

What to look for when the failing leg is SIP — dial-out to/from an external
SBC or PSTN gateway, a registered endpoint joining, or a SIP↔WebRTC gateway
call on the Pexip side.

SIP traces live primarily in `developer_log/` under `Name="support.sip"`
(or sometimes `Name="administrator.sip"` on the MN). Compact response-code
summaries also appear in `support_log/` against the participant lifecycle.

---

## Response code cheat sheet

Group by digit. The first digit tells you whose problem it is.

### 4xx — request failed, caller's side

| Code | Reason | Typical Pexip cause |
|---|---|---|
| **400** Bad Request | Malformed SIP — usually a missing required header (`To`, `From`, `Call-ID`, `Via`, `CSeq`). | SBC stripped a header; Pexip's `Outbound Proxy` config misaligned with what the SBC expects. |
| **401** Unauthorized | Missing/invalid credentials, `WWW-Authenticate` challenge issued. | Registration: wrong password on the Device or wrong realm. Look for repeated 401 → REGISTER → 401 loops. |
| **403** Forbidden | Authentication succeeded but the resource is denied. | Identity allowed but the called alias is not exposed (`Call routing rule` not matched); ITSP-side number blocking. |
| **404** Not Found | Request-URI doesn't resolve at the next hop. | Wrong alias dialled; missing `Call routing rule`; SIP registrar doesn't know the destination. |
| **407** Proxy Authentication Required | Proxy challenge (vs. 401 from the UAS). | Outbound proxy expects auth; credentials missing on the SIP trunk. |
| **408** Request Timeout | No response within the SIP timer window. | DNS resolution succeeded but the target is unreachable / dropping; firewall rule blocking SIP signalling; far-end overloaded. |
| **480** Temporarily Unavailable | Endpoint reachable but not answering. | Registered endpoint offline or DND; voicemail not configured. |
| **486** Busy Here | Callee actively rejected. | User-busy. Maps to Pexip "reason=user_busy". |
| **487** Request Terminated | A pending INVITE was cancelled (caller hung up before the callee picked up). | Normal user behaviour — flag only if it's accompanied by an unexpected upstream CANCEL. |
| **488** Not Acceptable Here | SDP offer rejected by the UAS. | Codec / SRTP / RTCP-mux negotiation failed. Compare `m=` lines on offer vs. answer. |
| **491** Request Pending | Glare — both sides sent re-INVITE simultaneously. | Self-recovers via random backoff; only matters if it repeats. |

### 5xx — request failed, callee/server's side

| Code | Reason | Typical Pexip cause |
|---|---|---|
| **500** Server Internal Error | Generic — far-end SBC bug or misconfig. | Look at the `Reason:` header for clues; check far-end logs. |
| **503** Service Unavailable | Far-end refusing — overload or maintenance. | Often paired with `Retry-After`. Look for capacity issues at the SBC or licensing on the far side. |
| **504** Server Time-out | Far-end couldn't reach the next hop. | Cascade failure deeper in the SIP trunk. |

### 6xx — global failure

| Code | Reason | Typical Pexip cause |
|---|---|---|
| **603** Decline | Explicit decline (CallKit "Decline", DND policy). | Treat as user intent unless unexpected. |
| **604** Does Not Exist Anywhere | Authoritative "no such user". | Dialled alias is genuinely not provisioned anywhere. |

---

## Registration failures

A SIP-registered device (e.g. a meeting room endpoint registering to Pexip
as a registrar) cycles:

```
REGISTER → 401 (challenge) → REGISTER + Authorization → 200 OK
```

Failure patterns:

| Pattern | Root cause |
|---|---|
| `REGISTER → 401 → REGISTER → 401 → REGISTER → 401 …` (no 200) | Wrong password; or device computing the digest against the wrong realm. |
| `REGISTER → 403` | Device is denied entirely — `Device` not provisioned, or `IP allowlist` excludes its address. |
| `REGISTER → 408` | Registrar unreachable; check DNS SRV and firewall. |
| `REGISTER → 200` then re-registration short-cycles | NAT pinhole closing; lower `Min Re-Registration Period` or enable `nat=force_rport`. |
| `REGISTER → 503` | Registrar overloaded or licence exhausted (registered-endpoint licence is separate from port licence). |

Look in `administrator_log` for `Message="Device registration failed"` with
the `Reason` field, and cross-reference the source IP against the `Device`
config.

---

## INVITE / re-INVITE failures

A successful INVITE goes:

```
INVITE → 100 Trying → 180 Ringing (optional) → 200 OK → ACK → ... → BYE → 200 OK
```

Patterns to flag:

| Pattern | Diagnosis |
|---|---|
| `INVITE → 100 Trying → (nothing)` | Far-end accepted the INVITE but never proceeded. SBC bug, or downstream timeout. Check developer_log for `Transaction timer` events. |
| `INVITE → 183 Session Progress with SDP → (no 200)` | Early media set up but the call never connected. Often a far-side ring-back loop. The `Reason:` header on the eventual CANCEL says why. |
| `re-INVITE → 488` | SDP renegotiation mid-call rejected. Common when Pexip downshifts codecs or enables/disables BFCP and the peer doesn't support it. |
| `INVITE looping` (same Call-ID repeated 3+ times in seconds) | DNS round-robin sending to a dead endpoint; or a `Call routing rule` that points back to Pexip. |

### SDP negotiation diagnostics

Look for the offer/answer pair:

- **Codec mismatch**: every `m=audio` / `m=video` payload type in the
  offer must appear in the answer (or at least one common codec). A `488`
  with `Reason: Q.850;cause=88` (Incompatible Destination) is the canonical
  signal.
- **Missing media sections**: SBCs sometimes strip the `m=video` line —
  Pexip will mark the call as audio-only or fail depending on policy.
- **`a=sendonly` / `a=recvonly` mismatch**: one side declares sendonly, the
  other expects sendrecv. Look for `a=inactive` appearing where it
  shouldn't.
- **`a=rtcp-mux` asymmetry**: Pexip uses mux; some legacy SBCs don't.
  Negotiation fails silently in some Pexip versions.
- **TLS-SDP / SRTP profile mismatch**: `RTP/SAVP` vs. `RTP/SAVPF` vs.
  `UDP/TLS/RTP/SAVPF` — they don't interop.

---

## TLS / SRTP handshake failures

For TLS-signalling SIP (port 5061):

- `TLS handshake failed: certificate_unknown` → far-end doesn't trust
  Pexip's cert. Check the `Trusted CA` config on the SBC.
- `TLS handshake failed: handshake_failure` → cipher suite mismatch.
  Pexip may have negotiated TLS 1.2 only while the peer wants TLS 1.0.
- `TLS handshake failed: bad_certificate` → cert expired or hostname
  mismatch. Check `Server cert` and `SAN` entries.

For SRTP media:

- `SRTP profile not supported` in 488 reason phrase → DTLS-SRTP (RFC 5764)
  vs. SDES-SRTP (RFC 4568) mismatch. Pexip prefers DTLS-SRTP for WebRTC
  legs, SDES for legacy SIP.

---

## DNS

DNS failures show up as **408 Request Timeout** or as a SIP-layer
"connection failed" before any signalling reaches the wire. Look for:

- `support.dns` log lines with `Result="NXDOMAIN"` or `Result="SERVFAIL"`.
- Repeated failed lookups in a short window — often a misconfigured SRV
  record (`_sip._udp.example.com` pointing nowhere) or an internal
  resolver being unreachable.

Pexip caches DNS results; a recently-changed SRV can hit a stale cache.
Restarting the conferencing service or waiting out the TTL fixes it.

---

## REFER / NOTIFY (transfer)

When a SIP transfer occurs (e.g. an attendant transferring a caller into
a VMR):

```
REFER (with Refer-To header) → 202 Accepted → NOTIFY (sipfrag) … → final state
```

Failure patterns:

- `REFER → 405 Method Not Allowed` — the peer doesn't support transfer.
- `REFER → 202 Accepted` then no NOTIFY — peer accepted but never enacted.
  Often a B2BUA that doesn't proxy REFER properly.
- `NOTIFY` with `SIP/2.0 4xx` sipfrag body — the transfer target rejected.
  Read the sipfrag for the actual response.

---

## Early media (183 Session Progress)

`183 Session Progress` carries SDP for early media (ring-back tone from
the carrier, IVR prompts). If a call shows `183 → CANCEL` without `200 OK`,
the caller heard ringback then gave up — not a Pexip failure, usually a
called-party issue. Flag only if the `Cancel-Reason` or upstream BYE has
an unexpected reason like `Q.850;cause=41` (Temporary Failure).

---

## Reason-phrase mapping

Pexip surfaces SIP failures in admin log lines like:

```
Message="Call failed" reason="user_busy" Reason-Code="486"
```

Common reason phrases and what they mean:

| Pexip reason | Underlying |
|---|---|
| `user_busy` | 486 Busy Here |
| `unallocated_number` | 404 Not Found |
| `incompatible_destination` | 488 Not Acceptable Here |
| `temporary_failure` | 503 Service Unavailable |
| `normal_clearing` | 200 OK to BYE — normal hang-up |
| `call_rejected` | 603 Decline |
| `network_out_of_order` | 5xx from upstream |

---

## When SIP logs are absent

If the user supplies only `support_log/` and the failure is SIP-side,
you'll see only the **outcome** (`Message="Call failed"` + reason) but
not the wire trace. Say so explicitly and ask for `developer_log/` for
the same node + time window.
