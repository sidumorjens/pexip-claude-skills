---
name: pexip-call-rca
description: >
  Expert root cause analysis for Pexip Infinity call failures. Use this skill
  whenever the user asks to diagnose, debug, RCA, or analyse a Pexip call from
  Management Node / Conferencing Node logs — whether supplied as a support
  snapshot tarball/zip, a folder of per-node *.txt / *.log files, or a single
  concatenated support log. Triggers on questions about SIP failures
  (registration, INVITE/re-INVITE, SDP, TLS, REFER, SUBSCRIBE), WebRTC
  failures (ICE, DTLS, STUN/TURN, codec negotiation, WSS), and
  Pexip-specific patterns (license limits, locked VMR, BFCP, gateway
  bridging, media-node availability). Also fires when the user pastes raw
  Pexip log lines and asks "what went wrong" or "what does this mean".
  Use this skill — Pexip logs span multiple components (support.rest,
  support.ice, support.sip, administrator.conference, support.participant,
  support.crypto.keys, support.media) and the failure mode is often a chain
  of events across nodes, not a single error line.
---

# Pexip Infinity Call RCA — Expert Skill

Diagnose Pexip Infinity call failures from raw logs. The skill walks the input
(snapshot tarball, folder, or single file), runs a parser to extract a
per-call timeline plus any error/warning lines, then performs structured root
cause analysis against the bundled domain knowledge.

> **Persona for the reasoning step:** You are an expert Pexip Infinity network
> engineer specialising in SIP and WebRTC call diagnostics.

---

## Quick decision tree

| If the user asks about… | Read first |
|---|---|
| What the log fields mean / which component logs what | `references/log-format.md` |
| A SIP-side issue (SIP URI dial-out, registration, gateway call, response codes) | `references/sip-failures.md` |
| A WebRTC-side issue (browser/webapp client, ICE, DTLS, STUN/TURN) | `references/webrtc-failures.md` |
| A Pexip-platform message (license, locked, "no media nodes", BFCP, REFER, gateway-bridge) | `references/pexip-patterns.md` |
| What the RCA output should look like | `templates/rca-report.md` |

---

## 1. Workflow

Follow these steps **in order**. Do not skip the parser step — running the
model directly over raw logs wastes context and misses cross-file correlation.

### Step 1 — Identify the input shape

Ask the parser what it's looking at:

- **Tarball / zip** (Pexip "Support snapshot" download — typical filename
  `diagnostic_snapshot_*.tar.gz` or `*.zip`): extract to a temp dir, the
  parser handles this.
- **Folder of files**: typically `support_log/`, `developer_log/`,
  `administrator_log/` subdirs each containing per-node files. Sometimes
  flat — one file per node.
- **Single concatenated file**: the user has already merged or `cat`-ed
  multiple files together. Treat as one stream.
- **Pasted snippets in the conversation**: write them to a temp file and
  treat as Single file.

If unclear, run `file <path>` and `head -3 <path>` to confirm format.

### Step 2 — Run the parser

Invoke the bundled parser to produce a structured summary:

```bash
python3 <skill-dir>/scripts/parse_pexip_logs.py <path>
```

`<skill-dir>` is the folder containing this SKILL.md — typically
`~/.claude/skills/pexip-call-rca/` for a user install, or
`<project>/.claude/skills/pexip-call-rca/` for a project install. If you're
not sure where it landed, `find ~/.claude -name parse_pexip_logs.py 2>/dev/null`
will locate it.

The parser outputs JSON with this shape:

```json
{
  "input": { "kind": "tarball|folder|file", "path": "..." },
  "summary": {
    "total_lines": 1234,
    "time_span": ["2026-05-14T23:38:44Z", "2026-05-14T23:39:20Z"],
    "levels": { "INFO": 97, "WARNING": 0, "ERROR": 0 },
    "components": { "support.rest": 45, "support.ice": 32, ... }
  },
  "calls": [
    {
      "call_id": "e15d0b7a-...",
      "conference": "main-vmr",
      "conference_id": "fc00942c-...",
      "participants": [{ "id": "...", "name": "...", "protocol": "WebRTC", "remote_address": "10.0.1.12" }],
      "start": "2026-05-14T23:38:44.061Z",
      "end": "2026-05-14T23:39:20.669Z",
      "duration_s": 36.6,
      "disconnect_reason": "User initiated disconnect",
      "timeline": [
        { "ts": "...", "phase": "signaling|ice|crypto|media|disconnect", "event": "...", "evidence_line": 12 }
      ],
      "errors": [],
      "warnings": [],
      "ice": { "local_candidates": N, "remote_candidates": M, "selected_pair": {...} },
      "media": { "audio": {...}, "video": {...}, "presentation": {...} },
      "crypto": { "srtp_suite": "AES_CM_128_HMAC_SHA1_80" }
    }
  ],
  "orphan_errors": [ /* lines we couldn't pin to a call */ ]
}
```

### Step 3 — Classify each call

For each call in `calls[]`:

1. **Identify call type**: `SIP`, `WebRTC`, or `Mixed` gateway call. Use the
   `Protocol` field on the join/participant events and the component names
   that fire — `support.sip` for SIP legs, `support.ice` + `support.rest`
   for WebRTC legs. A call is **Mixed** if more than one Protocol appears
   for the same `Conference-ID` with different participants legged in.
2. **Locate the earliest anomaly**. Order events by timestamp. The first
   `Level="ERROR"` is the obvious candidate; in its absence look for the
   first WARNING, or for a state transition that never completes (e.g.
   ICE local candidates gathered but no `new-selected-pair`, or media
   streams created but no `New encryption suite`).
3. **Trace the causal chain** forward and backward from that anomaly.
   Pexip failures usually surface downstream of their root — e.g. an ICE
   failure can be a symptom of an upstream STUN/TURN reachability problem,
   or a 488 Not Acceptable Here downstream of a missing codec in the SDP
   offer.

### Step 4 — Handle the "no failure found" case explicitly

If the call has zero ERROR/WARNING lines **and** completed all expected
phases (signaling → ICE selected-pair → SRTP suite → media flowing →
clean disconnect), report:

> **Result:** Call completed normally. No anomalies detected.
> **Disconnect reason:** `<reason from log>`.
> **Evidence:** [list of phase-completion log lines].

Do **not** fabricate root causes for healthy calls. If the user expected
a failure and the log doesn't show one, point that out — they may have
the wrong log file, the wrong time window, or the failure was on a peer
node not included in the snapshot.

### Step 5 — Produce the RCA report

Output using `templates/rca-report.md`. It enforces a fixed shape:

- Call type & metadata
- Timeline (compact, with evidence line numbers)
- Root causes, ranked by likelihood
- Per-cause: evidence lines + remediation + confidence (high / medium / low)
- Open questions / what additional data would raise confidence

Each cited evidence line must include the **source file path** and **line
number** so the user can navigate to it. The parser preserves these.

---

## 2. What the parser does (and does not) do

The parser is intentionally **dumb**. It:

- Tokenises `Key="value"` and `Key='value'` log fields.
- Groups events by `Call-Id` and `Conference-ID`.
- Builds a per-call timeline with phase tags (signaling / ice / crypto / media / disconnect).
- Pulls out `Level="ERROR"` and `Level="WARNING"` lines verbatim with file:line citations.
- Extracts ICE candidate gathering, selected pair, SRTP suite, media stream
  stats, disconnect reason and duration.
- Picks out SIP response codes from `Name="support.sip"` / `Name="administrator.sip"`
  lines, including reason phrases.

It does **not** decide what failed. RCA reasoning is the model's job — the
parser just makes that job tractable.

If the parser exits non-zero or its JSON is empty, fall back to reading the
log directly (use `grep -nE 'Level="(ERROR|WARNING)"'` then `Read` for
surrounding context). Note the fallback in the report.

---

## 3. Output contract

Always produce both:

1. **Headline** (one sentence): call type, outcome, primary root cause if any.
2. **Structured report** following `templates/rca-report.md`.

For multi-call snapshots, produce one report per failed call. For successful
calls, list them in a brief appendix at the end (`call_id`, duration,
participants) — don't repeat the structured template for healthy calls.

When citing evidence, use the format `path/to/file.txt:42` so it's
clickable. The parser provides absolute paths; preserve them.

---

## 4. Common pitfalls (read before answering)

- **A clean log can look like a failure.** A WebRTC join generates dozens of
  `ICE setting remote candidate` lines as the client trickles candidates.
  Those are normal. The signal is the **absence** of `ICE new-selected-pair`,
  not the presence of many candidates.
- **`License-Type="None"` on disconnect is normal** for the API leg of a
  WebRTC join — the actual media leg consumes the port license. Don't flag it.
- **Participant joins twice.** A WebRTC client first joins with `Protocol="API"`
  (signaling-only token request) and then a second `Participant has joined`
  event fires with `Protocol="WebRTC"` once the media call is established.
  Two participant UUIDs for one human is expected. The API-leg
  Participant-Id equals the Call-Id.
- **The presentation stream often shows `a=inactive`** at SDP exchange when
  no one is sharing — not a failure.
- **`Local-Candidate-Port` is the same across multiple candidate types**
  on the Conferencing Node — Pexip multiplexes. This is not a port collision.
- **One missing component does not mean one missing capability.** A snapshot
  may include `support_log/` but not `developer_log/`. SIP signalling
  details live in `developer_log/` — say so if it's absent and reduces
  your confidence.
- **Timestamps span two formats per line**: ISO 8601 with offset (the
  first field) and a Python-style `YYYY-MM-DD HH:MM:SS,mmm` (the second).
  They are the same instant. Use the ISO one for sorting.

---

## 5. When to ask the user

Ask before answering if:

- The path doesn't exist or contains zero log files.
- The parser finds no `Call-Id` matching what the user described.
- Logs span multiple unrelated calls and the user didn't name one — ask
  which call to focus on, or offer to RCA the first failed one.
- The failure is plausibly on a peer system (SBC, IDP, browser) not visible
  in the supplied logs — say so explicitly and ask for the missing piece.

Do **not** ask before running the parser. Run it first, then ask if the
output is ambiguous.
