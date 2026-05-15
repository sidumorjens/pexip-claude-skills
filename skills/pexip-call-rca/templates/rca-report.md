# RCA report template

Produce **one report per failed call**. For successful calls in the same
snapshot, summarise in a brief appendix (see end). Fill every section. If a
section genuinely has nothing to say, write `_None observed._` rather than
omitting it.

Cite evidence as `path/to/file.txt:42`. Paths must be the **absolute** ones
the parser emitted so they're clickable from the user's IDE.

---

## Headline

> _One sentence: `<call-type>` call `<outcome>`. Primary cause: `<short>`._

Example:
> WebRTC call failed at ICE phase. Primary cause: no relay candidates because TURN was not configured for the Sydney location.

---

## Call metadata

| Field | Value |
|---|---|
| Call type | `SIP` / `WebRTC` / `Mixed gateway` |
| Conference | `<alias>` (`<Conference-ID>`) |
| Call-Id | `<uuid>` |
| Participant(s) | `<name>` (`<Participant-Id>`, `<protocol>`, from `<remote_address>`) |
| Start | `<iso timestamp>` |
| End | `<iso timestamp>` or `—` if call never connected |
| Duration | `<seconds>s` or `—` |
| Disconnect reason | exact `Detail` string, or `—` if never disconnected cleanly |
| Conferencing node(s) involved | `<node ip / id>` |
| Logs analysed | `<count> file(s) across <count> directory(ies)` |

---

## Timeline

Compact. One line per significant event. Times relative to call start in
parentheses. Phase tags in bold.

```
T+0.000s   **signaling**  Participant attempting to join (main-vmr)            support_log/cn1.txt:1
T+0.043s   **signaling**  API leg joined                                       support_log/cn1.txt:3
T+0.086s   **signaling**  POST /calls with WebRTC SDP offer                    support_log/cn1.txt:12
T+0.246s   **ice**        First local candidate (host udp)                     support_log/cn1.txt:16
T+0.330s   **ice**        First remote candidate (host udp, 10.211.55.2)       support_log/cn1.txt:43
T+0.452s   **ice**        Selected pair (host udp ↔ host udp)                  support_log/cn1.txt:85
T+1.266s   **crypto**     SRTP suite AES_CM_128_HMAC_SHA1_80                   support_log/cn1.txt:88
T+0.299s   **media**      VP9 720p@30 activated on stream 1 (video)            support_log/cn1.txt:31
T+36.573s  **disconnect** User initiated disconnect                            support_log/cn1.txt:93
```

Stop the timeline at the failure event; include the **next 2-3 lines after
the failure** if they're informative (e.g. a disconnect with reason).

---

## Root causes

Ranked **most likely first**. For each, fill the four fields below.

### 1. `<one-line root cause>`

**Confidence:** high / medium / low

**Evidence:**

- `path/to/file.txt:42` — quote the line (or the salient portion).
- `path/to/file.txt:57` — quote.
- Cite as many lines as the chain requires. Aim for 2-5; more is fine
  when correlation across files matters.

**Why this is the cause:**

Two to four sentences. Connect the evidence lines into a chain: this
happened → then this → which caused the failure. Reference the relevant
Pexip subsystem and what its expected behaviour is. Pull in domain
knowledge from the bundled references where it adds explanatory power.

**Remediation:**

Concrete and actionable. "Check the network" is not a remediation;
"Add a TURN server entry at Platform > Locations > Sydney with shared
secret X and re-test by joining from the same client" is.

If remediation requires Pexip admin UI changes, give the exact
navigation path. If it requires firewall changes, name the ports and
direction. If it requires asking the user for more data (different
log file, browser dev tools, etc.), say what specifically.

### 2. `<alternative root cause>` _(if applicable)_

Same shape as above. Only include if it's a genuinely viable
alternative. Don't pad the list with weak candidates — listing four
unlikely causes makes the strong one harder to act on.

---

## What would raise confidence

If your top cause is **medium** or **low** confidence, list the
additional data that would let you commit to **high**. Examples:

- `developer_log/` for `<node>` between `<start>` and `<end>` — would
  show the SIP wire trace.
- The client's `chrome://webrtc-internals` dump from the failing browser
  session.
- A second call attempt with **Logging level = DEBUG** set on the
  Conferencing Node.
- `system_metrics/` for the conferencing node — would confirm or rule
  out CPU saturation.

If confidence is **high**, write `_Not needed._`.

---

## Notes & caveats

Anything else the user should know. Use sparingly. Examples:

- "The supplied snapshot only includes one Conferencing Node, but the call
  was bridged through two. The peer node's logs would change this
  analysis."
- "Direct media is enabled on this VMR. The affected participant's media
  path is not visible in these logs."
- "Healthy lookalikes: the call had 11 `ICE setting remote candidate`
  lines, which is normal trickle behaviour and not part of the failure."

---

## Appendix — other calls in the snapshot

| Call-Id | Conference | Protocol | Participant | Duration | Outcome |
|---|---|---|---|---|---|
| `e15d0…` | main-vmr | WebRTC | DENNIS J LORIST | 36.6s | normal disconnect |
| … | … | … | … | … | … |

Only include this table if the snapshot contained more than one call.
