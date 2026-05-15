# Pexip Infinity log format reference

Pexip Infinity emits three kinds of log most relevant for call RCA:

| Directory | Source | Contains |
|---|---|---|
| `support_log/` | Conferencing Node + Management Node | High-signal call lifecycle: REST API, ICE, participant, crypto, media |
| `developer_log/` | Conferencing Node | Per-stack chatter: SIP, H.323, WebSocket, full SDP, protocol traces |
| `administrator_log/` | Management Node | Configuration changes, admin actions, system events |

A **support snapshot** tarball typically contains all three, plus
`system_logs/`, `db_dumps/`, and per-node subdirectories.

---

## Line shape

Every log line follows this loose grammar:

```
<iso_timestamp> <node_id> <local_timestamp> Level="<LEVEL>" Name="<component>" Message="<one-line message>" <Key="value">*
```

Concrete example (from `support_log`, line numbers added):

```
2026-05-14T23:38:44.061+00:00 internal 2026-05-14 23:38:44,061 Level="INFO" Name="administrator.conference" Message="Participant attempting to join conference." ConferenceAlias="main-vmr" Participant="DENNIS J LORIST" Protocol="API" Direction="in" Remote-Address="10.0.1.12" Participant-Id="e15d0b7a-..." Location="syd"
```

### Field parsing rules

- Keys are **PascalCase-with-hyphens** (e.g. `Call-Id`, `Participant-Id`, `Service-Tag`, `Conference-ID`).
- Values are double-quoted. Inner double quotes are backslash-escaped.
- Some `Detail="..."` payloads contain a JSON blob (REST API request/response logging) — `\"` quoted JSON inside `"…"`.
- `Detail` may contain `^M` literally (CR), used as a line separator inside SDP, multi-line stats, or stack traces — treat `^M` as a logical newline within the field.

A robust regex for top-level KV extraction:

```regex
(\b[A-Za-z][A-Za-z0-9._-]*)="((?:[^"\\]|\\.)*)"
```

---

## Levels

In escalation order:

| Level | What it usually means |
|---|---|
| `DEBUG` | Verbose; appears in developer_log only |
| `INFO` | Normal lifecycle. The bulk of every log. |
| `WARNING` | Recoverable issue (one retry succeeded, codec downshift, etc.) |
| `ERROR` | The call or operation failed |

A healthy call may contain zero `WARNING`/`ERROR` lines. Treat their absence
as the default state, not as suspicious.

---

## Correlation IDs

| Field | Use |
|---|---|
| `Call-Id` | Primary key for a media call leg. Lives for the duration of the leg. |
| `Conversation-Id` | Equals `Call-Id` on the original leg; preserved across re-INVITEs. |
| `Participant-Id` | Pexip-internal participant UUID. **A single human can have two** — one for the API/signaling leg, one for the media leg. |
| `Conference-ID` | The VMR / conference instance UUID. Stable across participants in the same meeting. |
| `Uuid` | On REST API log lines, equals the API-leg Participant-Id. |

### Joining calls across files

When a snapshot contains both `support_log/` (per Conferencing Node) and
`developer_log/` (SIP/WebSocket traces), correlate by `Call-Id`. If the
peer side of a B2BUA / gateway call is logged, its `Call-Id` will differ —
match instead on `Conference-ID` plus near-identical timestamps.

---

## Components (Name field) you'll encounter

The `Name="…"` field tells you which subsystem emitted the line. Tags
prefixed with `support.` are the high-signal call-path components.

| Component | What it logs |
|---|---|
| `support.rest` | Every REST API request and response on the client v2 API (`/api/client/v2/...`). Token requests, candidate trickle, mute/unmute, disconnect. |
| `support.ice` | ICE candidate gathering, remote candidate setting, selected pair, state transitions. |
| `support.crypto.keys` | SRTP key negotiation and suite selection (e.g. `AES_CM_128_HMAC_SHA1_80`). |
| `support.media` | Per-stream codec mode changes ("New mode activated"), resolution/bitrate switches. |
| `support.participant` | Media stream create/destroy with codec, bitrate, loss, jitter summary. |
| `support.sip` | SIP signalling: INVITE, response codes, REFER. (Appears in developer_log primarily.) |
| `support.signaling` | Non-SIP signalling — WebSocket, registration. |
| `administrator.conference` | Conference- and participant-level lifecycle visible to admins: attempting to join, has joined, PIN entry, has disconnected. |
| `administrator.sip` | SIP-level admin events on the Management Node side. |
| `connectivity` | TCP/TLS reachability checks (often Management Node ↔ Conferencing Node). |

---

## Phase markers

Use these messages as **phase boundaries** when building a timeline:

| Phase | Marker message(s) |
|---|---|
| **Conference join attempt** | `Message="Participant attempting to join conference."` |
| **PIN / auth** | `Message="PIN entry correct."` / `Message="PIN entry incorrect."` / `Message="Authentication failed."` |
| **API leg joined** | `Message="Participant has joined."` with `Protocol="API"` |
| **Media call requested** | REST POST to `…/calls` |
| **ICE gathering** | `Message="ICE new-local-candidate event"` (multiple) |
| **ICE remote trickle** | `Message="ICE setting remote candidate"` (multiple) |
| **ICE complete** | `Message="ICE new-selected-pair event"` (per component) |
| **SRTP negotiated** | `Message="New encryption suite"` (encryption + decryption) |
| **Media flowing** | `Message="New mode activated"` — first per-stream codec activation |
| **Media call joined** | second `Message="Participant has joined."` with `Protocol="WebRTC"` or `Protocol="SIP"` |
| **Mid-call events** | `Message="Participant disconnect requested"`, mute/unmute, presentation grab, REFER |
| **Stream teardown** | `Message="Media Stream destroyed"` with embedded RX/TX/loss/jitter stats |
| **Participant disconnected** | `Message="Participant has disconnected."` with `Duration="…"` and `Detail="…"` |

The healthy WebRTC sequence is: join attempt → PIN → API joined → calls →
ICE gathered → ICE selected-pair → encryption suite → media modes → WebRTC
joined → (mid-call) → stream destroyed → disconnected.

A failure typically manifests as the sequence stalling — e.g. ICE
candidates gathered but no `new-selected-pair`, or `Media Stream created`
but no `New mode activated`, or a `Disconnect` event with a non-user
reason.

---

## Useful greps

```bash
# all errors and warnings
grep -nE 'Level="(ERROR|WARNING)"' <file>

# everything for one call
grep -F 'Call-Id="<uuid>"' <file>

# SIP response codes
grep -oE 'sip_response_code="[0-9]+"|status_code="[0-9]+"' <file> | sort | uniq -c

# ICE state transitions for one call
grep -F 'Call-Id="<uuid>"' <file> | grep -F 'Name="support.ice"'

# disconnect reasons
grep -F 'Message="Participant has disconnected."' <file> | grep -oE 'Detail="[^"]+"'
```

---

## Snapshot directory map

A standard Pexip support snapshot expands to something like:

```
diagnostic_snapshot_2026-05-14_<id>/
├── system_logs/
│   ├── <node-1>/
│   │   ├── support_log/
│   │   ├── developer_log/
│   │   └── administrator_log/   # only on the MN
│   └── <node-2>/
├── db_dumps/                    # config snapshot, ignore for RCA
└── system_metrics/              # node CPU/memory/network, useful for capacity issues
```

When the user supplies a snapshot, walk **all** `support_log/` and
`developer_log/` folders across all nodes — a failed call usually
touches both signalling (developer_log) and media-path (support_log)
nodes.
