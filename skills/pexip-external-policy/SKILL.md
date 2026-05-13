---
name: pexip-external-policy
description: >
  Expert knowledge for designing, building, and debugging Pexip Infinity External Policy servers
  and local policy scripts. Use this skill whenever the user is working with Pexip External Policy,
  local policy Jinja2 scripts, policy server implementations (Flask, FastAPI, Node.js), ABAC/attribute-based
  access control for VMRs, participant routing decisions, breakout rooms via policy, service configuration
  responses, participant policy responses, media location decisions, participant avatars, directory
  lookups, registration policy, IDP attributes, or policy proxy/engine architectures. Also triggers for
  questions about Policy Studio, pexip-policy-proxy, dial-out control, media policy enforcement, or any
  integration between Pexip Infinity and external identity/attribute systems. Use this skill — Pexip
  policy has many subtle gotchas, multiple request types each with their own fields, and the official
  docs are deep but easy to misread.
---

# Pexip Infinity External Policy — Expert Skill

Comprehensive knowledge for implementing Pexip Infinity External Policy servers. Captures field-level
detail for every request/response type from the Pexip docs, plus hard-won implementation knowledge
from building production policy servers, visual policy studios, ABAC enforcement, and breakout routing.

---

## Quick Decision Tree

**What is the user trying to do?**

| Goal | Read this first |
|---|---|
| Route a call based on the dialed alias / set VMR config | `references/service-configuration.md` |
| Override role, display name, role, audio mix, or reject a participant | `references/participant-properties.md` |
| Choose which Conferencing Node location handles media | `references/media-location.md` |
| Serve participant or directory avatar images (JPEG) | `references/participant-avatar.md` |
| Provide phonebook entries to registered Pexip apps | `references/directory-information.md` |
| Allow/deny device registration to Pexip | `references/registration-alias.md` |
| Build breakout rooms via policy | §5 below + `references/service-configuration.md` |
| Enforce ABAC / attribute-based controls | §6 below |
| Debug a non-working policy server | §8 below |

Each reference file contains the **complete** request parameter list, the **complete** response field
specification with types and defaults, and worked examples. The body of this SKILL.md covers the
shared concepts and the practical patterns that aren't in the docs.

---

## 1. How Pexip External Policy Works

A Pexip Conferencing Node sends an HTTP **GET** request to your policy server at specific call lifecycle
trigger points. Your server returns a JSON decision. Pexip acts on it immediately.

### Six Request Types

| Request type | When it fires | URI |
|---|---|---|
| **Service configuration** | Incoming call, or before dialing out to invite a participant | `/policy/v1/service/configuration` |
| **Participant properties** | After service config, before joining (after PIN/SSO for WebRTC; before PIN for SIP/H.323) | `/policy/v1/participant/properties` |
| **Media location** | After participant properties, to choose the media-handling Conferencing Node | `/policy/v1/participant/location` |
| **Participant avatar** | When a participant or directory avatar JPEG is needed | `/policy/v1/participant/avatar/<alias>` |
| **Directory information** | When a registered Pexip app does a directory lookup | `/policy/v1/registrations` |
| **Registration alias** | When a device tries to register to a Conferencing Node | `/policy/v1/registrations/<alias>` |

Each request type can be **individually enabled or disabled** in the policy profile (Call control >
Policy Profiles). Disabled request types fall back to Pexip's own database behaviour.

### Transport & Auth

- **GET only** — all request types use HTTP GET with parameters in the query string
- **HTTPS strongly recommended** in production
- **HTTP Basic Auth** (username/password set in the policy profile)
- **5 second timeout** — non-configurable. Slow servers get the fallback behaviour.
- **Content-Type** of `application/json` for responses (except avatar which is `image/jpeg`)
- **No 301/302 redirects** — Pexip will not follow them
- Length limit on response fields: **250 characters** per field

### Common Response Envelope

All responses except participant avatar follow this shape:

```json
{
  "status": "success",
  "action": "reject|redirect|continue",
  "result": { ... data ... },
  "<other_key>": "<other_value>"
}
```

- `"status": "success"` is **mandatory**. Anything else means failure → Pexip falls back to its database.
- `"action"` is interpreted differently per request type — see each reference file.
- `"result"` is the data payload — schema depends on request type.
- Extra keys are allowed; they don't affect processing but appear in support logs (useful for `"reason"` or version markers).

### Two-stage WebRTC join

When a Pexip app joins via WebRTC, you'll see **two participant requests in quick succession**:
first with `participant_type=api`, then `participant_type=standard`. The `api_host` variant of the
first means "this api participant should also start the conference if Host". Decide whether you want
your policy logic to apply to both or only `standard`.

---

## 2. Field Categories (Common Across Request Types)

The docs define a single global parameter table referenced by every request type. Here are the
categories of fields you'll see across multiple request types — see each reference file for which
fields each request type actually includes.

### Identity & call routing

`local_alias`, `remote_alias`, `remote_display_name`, `remote_address`, `remote_port`, `protocol`,
`call_direction`, `call_tag`, `vendor`, `registered`, `trigger`

### Service identification (set after service_configuration response)

`service_name`, `service_tag`, `unique_service_name`, `previous_service_name`, `breakout_uuid`

### Conferencing Node context

`location`, `node_ip`, `proxy_node_address`, `proxy_node_location`, `version_id`, `pseudo_version_id`

### Identity Provider (WebRTC SSO only)

`idp_uuid`, `has_authenticated_display_name`, `idp_attribute_<name>` (one query param per custom IdP attribute)

### Participant lifecycle (participant properties only)

`participant_uuid`, `call_uuid`, `participant_type`, `preauthenticated_role`, `display_count`,
`receive_from_audio_mix`, `send_to_audio_mixes_mix_name`, `send_to_audio_mixes_prominent`

### SIP-specific (only in SIP-triggered requests)

`ms-subnet`, `p_Asserted-Identity` — note: hyphenated in the wire format, but `ms_subnet` and
`p_asserted_identity` (underscore + lowercase) when accessed in local policy. Values arrive as JSON lists.

### Microsoft Teams / external integrations

`teams_tenant_id`, `third_party_passcode`, `telehealth_request_id`, `supports_direct_media`

> For the full table showing which parameters appear in which request type, see the
> "Summary of request parameters per request type" section at the bottom of
> https://docs.pexip.com/admin/external_policy_requests.htm

---

## 3. The Six Service Types

A `service_configuration` response returns one of six service types. The required and optional
response fields differ between them. See `references/service-configuration.md` for the full field
tables for each.

| `service_type` | What it is |
|---|---|
| `"conference"` | A Virtual Meeting Room (VMR) |
| `"lecture"` | A Virtual Auditorium (Host/Guest with separate views) |
| `"gateway"` | An Infinity Gateway call (incoming → outgoing protocol transform) |
| `"two_stage_dialing"` | A Virtual Reception (IVR with DTMF entry to choose target) |
| `"media_playback"` | A Media Playback Service (plays a playlist) |
| `"test_call"` | A Test Call Service |

---

## 4. Implementing a Policy Server

### Minimal FastAPI Skeleton (all six request types)

```python
from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse, Response
import secrets
import os

app = FastAPI()
security = HTTPBasic()

POLICY_USER = os.environ["POLICY_USER"]
POLICY_PASS = os.environ["POLICY_PASS"]

def check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    if not (secrets.compare_digest(credentials.username, POLICY_USER) and
            secrets.compare_digest(credentials.password, POLICY_PASS)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            headers={"WWW-Authenticate": "Basic"})

@app.get("/policy/v1/service/configuration")
async def service_configuration(request: Request, _=Depends(check_auth)):
    params = dict(request.query_params)
    # See references/service-configuration.md
    return JSONResponse({"status": "success", "action": "continue", "result": {}})

@app.get("/policy/v1/participant/properties")
async def participant_properties(request: Request, _=Depends(check_auth)):
    params = dict(request.query_params)
    # See references/participant-properties.md
    return JSONResponse({"status": "success", "action": "continue", "result": {}})

@app.get("/policy/v1/participant/location")
async def media_location(request: Request, _=Depends(check_auth)):
    params = dict(request.query_params)
    # See references/media-location.md
    return JSONResponse({"status": "success", "result": {}})

@app.get("/policy/v1/participant/avatar/{alias:path}")
async def participant_avatar(alias: str, request: Request, _=Depends(check_auth)):
    # See references/participant-avatar.md — must return image/jpeg
    return Response(status_code=404)

@app.get("/policy/v1/registrations")
async def directory_information(request: Request, _=Depends(check_auth)):
    params = dict(request.query_params)
    # See references/directory-information.md
    return JSONResponse({"status": "success", "result": []})

@app.get("/policy/v1/registrations/{alias:path}")
async def registration_alias(alias: str, request: Request, _=Depends(check_auth)):
    params = dict(request.query_params)
    # See references/registration-alias.md
    return JSONResponse({"status": "success", "action": "continue", "result": {}})

@app.get("/health")
async def health():
    return {"status": "ok"}
```

### Docker Compose Pattern

```yaml
services:
  policy-server:
    build: .
    environment:
      - POLICY_USER=pexip
      - POLICY_PASS=changeme
      - ENTRA_TENANT_ID=...
      - ENTRA_CLIENT_ID=...
      - ENTRA_CLIENT_SECRET=...
    expose:
      - "8080"

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - policy-server
```

### Nginx Reverse Proxy (with SSE for live logs)

SSE endpoints need buffering disabled. **Nested `location` blocks do not work** in Nginx — the
inner block is silently ignored. Use top-level blocks, ordered most-specific first:

```nginx
server {
    listen 443 ssl;
    server_name policy.example.com;

    ssl_certificate     /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;

    # SSE — MUST be a top-level location, BEFORE any broader /admin/ block
    location /admin/logs {
        proxy_pass         http://policy-server:8080;
        proxy_buffering    off;
        proxy_cache        off;
        proxy_read_timeout 3600s;
        proxy_http_version 1.1;
        chunked_transfer_encoding on;
    }

    location /admin/ {
        proxy_pass       http://policy-server:8080;
        proxy_set_header Host $host;
    }

    # Use $request_uri to preserve URL-encoded characters like %40
    location /policy/ {
        proxy_pass       http://policy-server:8080$request_uri;
        proxy_set_header Host $host;
    }

    location /health {
        proxy_pass http://policy-server:8080;
    }
}
```

---

## 5. Breakout Rooms via Policy

Breakout rooms are sub-conferences inside a parent VMR. They are how you build per-participant
waiting rooms, host-controlled admit flows, and topic-specific sub-meetings. The breakout fields
(`breakout`, `breakout_uuid`, `breakout_name`, etc.) live in the `service_configuration` response —
see the "Breakout room fields" section of `references/service-configuration.md`.

### Critical: prefer local policy (Jinja2) for breakout creation

External policy can create breakouts, but Pexip's internal merge/validation of the `name` field
(which it looks up in its DB) conflicts with dynamically generated breakout UUIDs in some scenarios.
Local policy runs after the DB lookup with direct access to the internal data model — it's the
approach used in Pexip's own examples and is significantly more reliable.

### Pattern: per-guest waiting room via unknown alias

A guest dials an alias that does **not** exist as a configured VMR. Local policy intercepts and creates
a per-participant breakout under the parent VMR. The guest sits in the waiting room until a Host in
the parent VMR admits them.

In Pexip admin: **Call control > Policy Profiles > Service configuration > Apply local policy**

```jinja2
{
    {% if service_config %}
        "action" : "continue",
        "result" : {{service_config|pex_to_json}}
    {% else %}
        {% if call_info.local_alias.startswith("your-guest-alias") %}
            "action" : "continue",
            "result" : {
                "name": "your-main-vmr",
                "service_type": "conference",
                "service_tag": "lobby_{{ call_info.remote_alias }}",
                "breakout": true,
                "breakout_uuid": "{{ call_info.remote_alias | pex_hash }}",
                "breakout_name": "Waiting Room - {{ call_info.remote_display_name or call_info.remote_alias }}",
                "breakout_description": "Please wait, you will be admitted shortly",
                "end_action": "transfer",
                "end_time": 0,
                "allow_guests": true,
                "pin": ""
            }
        {% else %}
            "action" : "reject",
            "result" : {}
        {% endif %}
    {% endif %}
}
```

**Key requirements:**
- The guest alias (`your-guest-alias`) must **not** be configured as a VMR in Pexip's database
- The parent VMR (`your-main-vmr`) **must** exist in the database
- `pex_hash` creates a deterministic UUID from any string — same caller → same breakout room
- The `{% else %}` branch fires for unknown aliases — this is where you catch the guest dial pattern

### Pattern: multiple host-triggered breakouts

When responding to the main VMR with `breakout_uuids: [uuid1, uuid2, uuid3]`, the Host attempts to
join each of those breakouts as a control-only participant. Each triggers a new policy lookup with:

- `service_name: "<main_room_name>_breakout_<breakout_uuid>"`
- `unique_service_name`: same as `service_name`
- `breakout_uuid`: the UUID being created

Your policy must respond to each of those with a breakout-room configuration block.

---

## 6. ABAC (Attribute-Based Access Control)

### Receiving IdP attributes

When a Webapp3 user authenticates via SAML/OIDC, the Identity Provider's custom attributes arrive in
the participant policy request as **individual query parameters**, each prefixed with `idp_attribute_`.

If your IdP exposes attributes `clearance` and `groups`, they arrive as:
```
&idp_attribute_clearance=SECRET&idp_attribute_groups=role1&idp_attribute_groups=role2
```

Configure which IdP attributes get exposed under **Users & Devices > Identity Providers > Advanced
options** in Pexip admin.

```python
# Collect all idp_attribute_* keys from the query string
idp = {
    k.removeprefix("idp_attribute_"): request.query_params.getlist(k)
    for k in request.query_params.keys()
    if k.startswith("idp_attribute_")
}
clearances = idp.get("clearance", [])
groups = idp.get("groups", [])
```

### Timing of IdP attributes

| Endpoint type | IdP attributes available? |
|---|---|
| WebRTC + SSO | ✅ Yes — participant policy fires after SSO |
| WebRTC + PIN only | ❌ No IdP attributes; `preauthenticated_role` may be `chair`/`guest` after PIN |
| SIP / H.323 | ❌ No IdP attributes; participant policy fires **before** PIN entry |
| MS Teams gateway | Use `teams_tenant_id` to scope decisions |

### What External Policy CAN and CANNOT Enforce

| Capability | Via External Policy | How |
|---|---|---|
| Reject join | ✅ Yes | `action: "reject"` in service_configuration OR participant_properties |
| Redirect to another alias | ✅ Yes | `action: "redirect"` + `result.new_alias` in service_configuration |
| Set role (host/guest) | ✅ Yes | `result.preauthenticated_role` in participant_properties |
| Override display name | ✅ Yes | `result.remote_display_name` in participant_properties |
| Override alias | ✅ Yes | `result.remote_alias` in participant_properties |
| Bypass locked conference | ✅ Yes | `result.bypass_lock: true` in participant_properties |
| Disable participant text overlay | ✅ Yes | `result.disable_overlay_text: true` in participant_properties |
| Block receive presentation | ✅ Yes | `result.rx_presentation_policy: "DENY"` in participant_properties (UPPERCASE) |
| Personal layout enable | ✅ Yes | `result.can_receive_personal_mix: true` |
| Audio mix routing | ✅ Yes | `result.receive_from_audio_mix` / `result.send_to_audio_mixes` |
| Spotlight priority | ✅ Yes | `result.spotlight` (integer; lower = higher priority) |
| Layout group (pinning) | ✅ Yes | `result.layout_group` |
| Per-participant audio/video mute (TX) | ❌ No native | Use Management API mid-call |
| Per-participant audio/video mute (RX) | ❌ No native | Architect via separate VMRs + transfer |
| Mid-call disconnect | ❌ No | Use Management API |
| Mid-call transfer | ❌ No | Use Management API |
| Mid-call role change | ❌ No | Use Management API |

### Mid-call enforcement via Management API

```python
import httpx

async def disconnect_participant(mgmt_url: str, auth: tuple, participant_id: str):
    async with httpx.AsyncClient(verify=False) as client:
        return await client.post(
            f"{mgmt_url}/api/admin/command/v1/participant/disconnect/",
            data={"participant_id": participant_id}, auth=auth)

async def transfer_participant(mgmt_url, auth, participant_id, conference_alias, role="guest"):
    async with httpx.AsyncClient(verify=False) as client:
        return await client.post(
            f"{mgmt_url}/api/admin/command/v1/participant/transfer/",
            data={"participant_id": participant_id, "conference_alias": conference_alias, "role": role},
            auth=auth)
```

---

## 7. Dialing Out — Important Restrictions

When Pexip Infinity is dialing out from an existing conference (`call_direction=dial_out`):

- **service_configuration** still fires, but the response **must match the existing service data** —
  the same `name`, `service_type`, etc. You cannot redirect a dial-out to a different VMR.
- The only fields you can actually control on dial-out are:
  - `prefer_ipv6` in the service_configuration response
  - The media location in the subsequent media_location response

This is why ABAC enforcement on outbound calls has to happen at a different layer (e.g. preventing
the dial-out via Management API rather than rejecting it in policy).

---

## 8. Debugging Checklist

### Silent failure modes

| Symptom | Likely cause |
|---|---|
| Policy ignored, Pexip uses DB config | Missing `"status": "success"` in response |
| Always falls back to default | Response not Content-Type `application/json`, or returned non-2xx |
| Policy server never gets requests | Policy profile not assigned to the location; or request type disabled in profile |
| Auth failing | Basic Auth credentials don't match what's in the policy profile |
| `service_configuration` not firing for known VMR | This is normal — by default policy only fires for unknown aliases. Enable "external policy for known services" if needed |
| `idp_attributes` empty | Expected for SIP/H.323 and non-SSO WebRTC; participant policy fires before SSO for those |
| Breakout fails | `name` doesn't match a real VMR in DB; or using external where local policy works better |
| Sub-5s response not enough | The 5s timeout is non-configurable — cache external lookups (Graph, LDAP, DB) aggressively |
| Field values truncated | 250-character per-field limit; shorten descriptions and dynamic strings |
| Action=redirect not following | Must be `service_configuration` response; `result` must be `{"new_alias": "sip:..."}` |
| Multiple requests per WebRTC join | Normal — `participant_type=api` then `participant_type=standard` |

### Testing without Pexip

```bash
# service_configuration
curl -u user:pass "http://localhost:8080/policy/v1/service/configuration?call_direction=dial_in&protocol=webrtc&local_alias=meet.test@example.com&remote_alias=alice@example.com&remote_display_name=Alice&remote_address=10.1.1.5&location=Sydney&node_ip=10.1.1.1&version_id=39&pseudo_version_id=77683.0.0&trigger=web&registered=False&bandwidth=0&idp_uuid=&has_authenticated_display_name=False&supports_direct_media=False"

# participant_properties
curl -u user:pass "http://localhost:8080/policy/v1/participant/properties?call_direction=dial_in&protocol=webrtc&participant_uuid=a13e1e71-0000-0000-0000-000000000001&call_uuid=a13e1e71-0000-0000-0000-000000000001&preauthenticated_role=chair&participant_type=standard&service_name=my-vmr&service_tag=my-tag&local_alias=meet.test@example.com&remote_alias=alice@example.com&remote_display_name=Alice&location=Sydney&node_ip=10.1.1.1&version_id=39&idp_attribute_clearance=SECRET&idp_attribute_groups=guests&receive_from_audio_mix=main&send_to_audio_mixes_mix_name=main&send_to_audio_mixes_prominent=False"
```

### Built-in tools in Pexip admin

- **Local policy test facility** (Call control > Policy Profiles > test): paste a sample request,
  see exactly which path your Jinja2 takes and what JSON gets returned
- **Support log** (Status > Support Log): every policy decision is logged; the `<other_keys>` in
  your response (e.g. `"reason"`) appears here for forensics

### Always log every decision

```python
log.info("↓ %s uuid=%s local=%s remote=%s tag=%s",
         "participant_policy", params.get("participant_uuid"),
         params.get("local_alias"), params.get("remote_alias"),
         params.get("service_tag"))
# ... build decision ...
log.info("↑ %s → %s reason=%s",
         "participant_policy", decision["action"], decision.get("reason", "-"))
```

---

## 9. Quick Reference — Pexip Management API (for mid-call enforcement)

```
Base: https://<management-node>/api/admin/

# List active conferences
GET  configuration/v1/conference/

# List participants in a conference  
GET  status/v1/participant/?conference__name=<name>

# Disconnect a participant
POST command/v1/participant/disconnect/        body: {"participant_id": "<uuid>"}

# Transfer a participant to another conference
POST command/v1/participant/transfer/          body: {"participant_id": "<uuid>", "conference_alias": "<alias>", "role": "guest"}

# Change a participant's role mid-call
POST command/v1/participant/role/              body: {"participant_id": "<uuid>", "role": "chair|guest"}

# Send a chat message to a participant
POST command/v1/participant/message/           body: {"participant_id": "<uuid>", "payload": "<text>"}

# Unlock a participant held at "Waiting for Host"
POST command/v1/participant/unlock/            body: {"participant_id": "<uuid>"}

# Dial out a new participant into an existing conference
POST command/v1/participant/dial/              body: {"conference_alias": "...", "destination": "...", "role": "chair", "system_location": "..."}

# PATCH a conference/VMR
PATCH configuration/v1/conference/<id>/        body: {"<field>": "<value>"}
```

Auth: HTTP Basic with admin credentials. Use `verify=False` for self-signed certs in dev only.

---

## 10. Pre-flight Checklist for a New Policy Server

- [ ] All six endpoints implemented (or unused ones disabled in policy profile)
- [ ] All responses use HTTP GET handlers
- [ ] Every JSON response includes `"status": "success"`
- [ ] Avatar endpoint returns `Content-Type: image/jpeg` (not JSON)
- [ ] HTTP Basic Auth validated on every request
- [ ] `/health` endpoint returns 200
- [ ] All decisions complete within 5 seconds (cache slow lookups)
- [ ] Response field values fit within 250 characters
- [ ] Logging captures `participant_uuid`, `local_alias`, `service_tag`, `action` for every decision
- [ ] Policy profile assigned to the correct system locations in Pexip admin
- [ ] HTTPS in production with valid certificate chain
- [ ] Tested with curl against every endpoint before connecting Pexip
- [ ] Verified `idp_attribute_*` parsing for both individual params and JSON fallback
- [ ] Plan for mid-call enforcement gaps (use Management API where needed)
