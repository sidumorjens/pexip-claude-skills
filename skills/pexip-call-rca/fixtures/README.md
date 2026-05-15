# Test fixtures

Synthetic Pexip Infinity log excerpts that exercise the
[pexip-call-rca skill](../SKILL.md)'s RCA path.

These are **fabricated** — they reflect the documented log shape and the
failure modes in the bundled reference docs, but were not captured from a
live system. Field values, UUIDs, and IPs are illustrative.

Use them as quick acceptance tests when iterating on the skill or parser.

## Catalogue

| File | Call type | Expected primary cause | Key evidence the skill should cite |
|---|---|---|---|
| [`registration-401-loop.txt`](registration-401-loop.txt) | SIP registration | Wrong device password (digest mismatch) — five 401 challenges over 2 minutes, then Pexip blocks the device with 403. | `WARNING Name="administrator.sip" Reason="digest_mismatch"` lines, escalating to `ERROR Message="Device registration disabled after repeated authentication failures"`. |
| [`ice-no-selected-pair.txt`](ice-no-selected-pair.txt) | WebRTC | NAT traversal failed: only host candidates exchanged, TURN issued empty, all connectivity checks timed out. | Empty `"turn": []` in the token response; no `srflx`/`relay` candidates; two `WARNING Message="ICE connectivity check failure" Reason="check_timeout"`; final `ERROR Message="ICE failed" Reason="all_candidate_pairs_failed"`; disconnect `Detail="Call timed out"`. |
| [`codec-mismatch-488.txt`](codec-mismatch-488.txt) | SIP gateway | Far-end SBC offered H.265-only video on `RTP/SAVP`; Pexip has neither H.265 nor SAVP-without-feedback. Returns 488. | `WARNING Message="No common video codec"`; `WARNING Message="SRTP profile incompatible"`; `ERROR reason="incompatible_destination" Reason-Code="488"`; outbound SIP `Response="488"`. |
| [`vmr-locked.txt`](vmr-locked.txt) | WebRTC (token) | Host locked the VMR; new participants get HTTP 403 with `reason="conference_locked"`. Repeated retries. | `Locked="True"` in the conference state lookup; three `WARNING Message="Participant rejected" Reason="conference_locked"` with three different `Participant-Id`s and one `Remote-Address`. |
| [`license-exhausted.txt`](license-exhausted.txt) | Multiple | Port-license pool at 250/250 in use; two distinct conferences fail concurrently. | `WARNING Message="License check failed" Available-Port-Licenses="0"`; two `ERROR Message="License limit reached" Reason="port_limit_reached"`; HTTP 503 in the REST response. |

## Quick check

Run the parser against any fixture to confirm it picks up the failure
without errors:

```bash
python3 ../scripts/parse_pexip_logs.py registration-401-loop.txt --pretty | jq '.summary.levels, .calls[0].errors | length'
```

To exercise the full skill end-to-end, invoke Claude Code on a fixture
file and confirm:

1. The headline names the correct primary cause.
2. The structured report cites the actual `path/to/fixture.txt:N` lines
   listed in the table above.
3. Confidence is `high` on every fixture except `ice-no-selected-pair.txt`,
   which legitimately deserves `medium` until a TURN-side capture confirms
   the lack of relay candidates.
