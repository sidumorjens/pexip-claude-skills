# Skill Case Study: `pexip-external-policy`

A worked example of using the [`pexip-external-policy`](../../SKILL.md)
Claude skill to build the subnet → Pexip media-location policy server alongside
this document. Written from the perspective of evaluating how the skill
performs in practice — what it accelerated, where it had gaps, and what could
be added.

---

## 1. The prompts

Two turns produced everything in this repo.

**Turn 1 — original ask:**
> create a sample test external policy server using pexip-external-policy skill
> that allows me to create a map of IP subnets and Infinity locations for media
> policy. I should be able to allocate a media location based on the IP subnet
> and the location mapping

**Turn 2 — follow-up:**
> create a user interface so that I don't need to edit the subnet_map.json

The skill was invoked explicitly on turn 1 via the `pexip-external-policy`
slash skill. Turn 2 did not re-invoke the skill (the work was already in
session context), but it built on the architectural decisions the skill had
just driven.

---

## 2. Which parts of the skill carried the most weight

The skill's `SKILL.md` plus `references/media-location.md` were both read. Most
decisions in the resulting server trace directly to a specific section.

| Skill component | What it provided | Where it shows up |
|---|---|---|
| **SKILL.md §1** "How Pexip External Policy Works" | HTTP GET semantics, query-string params, the six request types, the `5s timeout`, `250-char field limit`, no-redirects rule | Drove the decision to implement all six endpoints (pass-through where not needed) so the server can be attached to a full policy profile without surprises. Also drove the "fast/cached" mental model — no slow lookups in `media_location`. |
| **SKILL.md §1** "Common Response Envelope" | `"status": "success"` is **mandatory**; missing it silently falls back to Pexip's database | The single most important nugget the skill encoded — easy to miss otherwise. Every response in [policy_server.py](policy_server.py) sets it. |
| **SKILL.md §4** FastAPI skeleton + Docker pattern | Concrete `Depends(check_auth)` shape, HTTPBasic + `secrets.compare_digest`, `/health` endpoint, JSONResponse usage | [policy_server.py:111-119](policy_server.py#L111-L119) — copied almost verbatim from the skeleton. Saved a full design pass. |
| **SKILL.md §8** Debugging checklist | "Always log every decision" + the silent-failure table | The structured log lines in [media_location](policy_server.py#L147-L176) (remote_ip, requesting_node_location, matched subnet, decision). Also why the response includes a `"reason"` key — the skill explicitly notes Pexip's support log surfaces extra keys for forensics. |
| **SKILL.md §10** Pre-flight checklist | "Avatar endpoint returns `Content-Type: image/jpeg`", "all six endpoints implemented (or unused ones disabled)", HTTPS in production | [participant_avatar](policy_server.py#L179-L182) returns 404 with no JSON body; pass-through endpoints exist for the four request types not used. The README's "Wire up in Pexip Infinity" section calls out the TLS termination requirement. |
| **references/media-location.md** | Exact `result` schema (`location` string + `overflow_locations` list); the **critical** note that an invalid location name fails the entire response | Drove the response shape in [media_location](policy_server.py#L147-L176) and the matching headline warning in [README.md](README.md) and the UI's intro text. The `default_location` + `default_overflow_locations` fallback design exists because the skill flags that returning an empty `result` is treated as invalid by some Pexip versions. |
| **references/media-location.md** "Geo-routing by participant IP" example | A 12-line snippet showing exactly the shape this project needed | The starting point for the resolver. The skill's example uses an undefined `geo_lookup()` function; this project filled that in with a real longest-prefix-match implementation using `ipaddress`. |

---

## 3. What the skill did NOT give us

Things the model had to bring independently because the skill's scope ended at
the policy protocol itself, not the data layer or operability around it.

| Gap | What was needed | What we did |
|---|---|---|
| **Subnet matching** | The skill's media-location reference shows a `geo_lookup()` placeholder but doesn't discuss longest-prefix match, IPv4/IPv6 handling, or how to structure the lookup data | Built a small `SubnetMap` class with `ipaddress.ip_network`, entries sorted by prefix length descending, and a deterministic tiebreak — [policy_server.py:46-95](policy_server.py#L46-L95) |
| **Hot reload** | Skill emphasises the 5s timeout (cache aggressively) but doesn't suggest a way to refresh cached config without restart | Added `POST /admin/reload` and made the editor's PUT reload automatically |
| **Config validation** | Skill is silent on validating policy *inputs* (the data the operator provides) — it only validates Pexip's response shape | Added Pydantic models with a `subnet` field validator that parses every CIDR before write. Locations are not validated against Pexip (no Management API call from this server) — see "Skill gaps worth filling" below. |
| **Atomic config write** | Out of scope for the skill | Tempfile in same dir + `os.fsync` + `os.replace`, with rollback on validation failure — [policy_server.py:271-291](policy_server.py#L271-L291) |
| **Web UI for editing** | Entirely outside the skill's stated scope | [admin_ui.html](admin_ui.html) — vanilla HTML/JS, same Basic Auth as the policy endpoints |

---

## 4. Skill output → repo file map

A quick index for evaluating which skill knowledge made it into the artifact.

| Repo file | Lines | Skill knowledge applied |
|---|---|---|
| [policy_server.py](policy_server.py) | imports + auth (1-119) | §4 FastAPI skeleton; §1 HTTPBasic; pre-flight checklist |
| [policy_server.py](policy_server.py) | `media_location` (147-176) | references/media-location.md schema + response envelope + `reason` key for support log |
| [policy_server.py](policy_server.py) | five pass-through endpoints (127-192) | §10 "all six endpoints implemented" + §8 "404 → Pexip falls back" |
| [policy_server.py](policy_server.py) | `SubnetMap` (46-95) | Filled in the skill's `geo_lookup()` placeholder |
| [policy_server.py](policy_server.py) | `/admin/*` + Pydantic (211-303) | Beyond skill scope |
| [admin_ui.html](admin_ui.html) | all | Beyond skill scope |
| [README.md](README.md) | "Wire up in Pexip Infinity" | §10 pre-flight + §1 transport/auth |
| [README.md](README.md) | "Critical" warning about location names | references/media-location.md "if any name is invalid, the entire response is deemed to have failed" |
| [subnet_map.json](subnet_map.json) | data | Beyond skill scope |

---

## 5. What worked well

- **The references/ split.** Loading the full media-location reference on demand (rather than baking field tables into SKILL.md) kept the initial skill load small but gave full-fidelity field details when needed. This is the right structure.
- **The "silent failure modes" table in §8.** This is the highest-leverage content in the skill — it encodes the unintuitive behaviour that takes hours to debug live. The `"status": "success"` requirement in particular shaped the whole response-building approach from the first response.
- **The FastAPI skeleton in §4.** Pre-written, correct, and uses the same `Depends(check_auth)` pattern across all six endpoints, so the resulting code is consistent without effort.
- **Mandatory-field tables in references/media-location.md.** The "Required: Yes/No" column and the worked examples meant zero guessing at JSON shape.
- **Calling out non-obvious constraints repeatedly.** The 5s timeout, 250-char field limit, and "name must match a configured location" appear in multiple places in the skill. That redundancy paid off — they got applied without re-reading.

---

## 6. Skill gaps worth filling

Things this build would have benefited from if they were in the skill:

1. **Worked end-to-end policy server examples.** The skill has a FastAPI *skeleton* but no full reference implementation of any single policy type. Adding `examples/media-location-subnet-router/` (essentially this repo, trimmed) would let future invocations point at concrete prior art instead of regenerating from primitives. **This case study is a first step toward that.**
2. **A "managing the policy data" section.** The skill exhaustively covers the *protocol* but is silent on how operators manage the data the policy decides on (subnet maps, IdP attribute ACLs, breakout configurations). A short section on patterns — file-backed JSON/YAML with hot reload, external DB, secrets manager — would help. Caching is mentioned for *external* lookups (Graph, LDAP) but not for *internal* config.
3. **Cross-validation against Pexip Management API.** The skill correctly warns that invalid location names fail the entire response, but doesn't suggest the obvious mitigation: at config-edit time, query the Management API's `configuration/v1/system_location/` to dropdown-validate names. Worth adding to §9 ("Quick Reference — Management API"). This server doesn't do that yet; a future iteration of the UI could.
4. **`overflow_locations` semantics.** The reference notes the field exists and that it's ordered, but doesn't explain *when* Pexip actually overflows. Is it on hard capacity? Soft? Per-call or per-conference? Operators editing these need to know — adding a paragraph from the Pexip admin docs would close the loop.
5. **A test-without-Pexip recipe per request type.** §8 has a curl example for `service_configuration` and `participant_properties` but not for `media_location`. The pattern is generalisable — every reference file could end with a "test it with curl" block.
6. **Atomic config writes.** Not Pexip-specific, but every policy server that lets operators edit config needs it. Worth a paragraph somewhere — operators sleeping on this will eventually hit a half-written JSON file at the worst moment.

---

## 7. Did skill use change my answer?

Almost certainly yes. Without the skill, the first turn would have started by
asking the user clarifying questions about Pexip's policy protocol, and the
first draft would likely have had at least one of:

- A missing `"status": "success"` field (the response would *look* valid but Pexip would silently ignore it)
- POST handlers instead of GET (the skill flags GET-only behaviour up front)
- An assumption that the avatar endpoint also returns JSON
- No `overflow_locations` support at all (it's optional but operationally important)

The skill collapsed the protocol-correctness work into "follow the template"
and let the conversation focus on the actual problem (subnet matching, then
UI). That's the right division of labour.

---

## 8. Reproducing

From this directory:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
POLICY_USER=pexip POLICY_PASS=changeme \
  uvicorn policy_server:app --host 127.0.0.1 --port 8080
# Open http://localhost:8080/  (browser will prompt for Basic Auth)
```

See [README.md](README.md) for full operational notes.
