# Registration Alias — Full Field Reference

**Request URI:** `GET /policy/v1/registrations/<alias>`

Used to determine whether a device alias is allowed to register to a Conferencing Node, and what credentials it needs to supply. The `<alias>` in the URL path is the alias the device is trying to register with (may include scheme — your server must parse this).

---

## Request Parameters

| Parameter | Description |
|---|---|
| `auth_type` | `"credentials"` (username/password required) or `"sso"` (single sign-on; no credentials needed). |
| `location` | Pexip system location of the Conferencing Node making the request. |
| `node_ip` | IP of the Conferencing Node. |
| `protocol` | Registration protocol: `"webrtc"`, `"sip"`, or `"h323"`. |
| `pseudo_version_id` | Pexip build number. |
| `remote_address` | IP of the registering device. |
| `version_id` | Pexip software version. |

### Example GET request

```
GET /example.com/policy/v1/registrations/alice@example.com
  ?pseudo_version_id=36402.0.0
  &protocol=webrtc
  &location=london
  &version_id=16
  &remote_address=10.44.151.5
  &node_ip=10.44.155.21
  &auth_type="credentials"
```

---

## Response Envelope

```json
{
  "status": "success",
  "action": "reject|continue",
  "result": { <alias_data> }
}
```

### `action` values for registration_alias

- **`"reject"`** — Pexip rejects the registration. `"result": {}` must also be included.
- **`"continue"`** (or anything else) — Pexip proceeds with the registration. If `result` provides credentials, those are used; otherwise Pexip falls back to its local database to validate the alias.

### `result` fields

| Field | Required | Description |
|---|---|---|
| `username` | No | Username associated with the device. |
| `password` | No | Password for the device/username. **Sent in clear text** — HTTPS is essential. |

Use `"result": {}` when:
- `auth_type` is `"sso"` (no credentials applicable)
- It's a rejection response
- You want Pexip to fall back to its own local DB of allowed aliases

### Status-driven fallback

- If `status` is not `"success"` (or HTTP 404 is returned), Pexip falls back to its **own default behaviour** (check the alias against its local DB).
- This is the recommended way to say "I don't know about this alias, please use your local DB."

---

## Worked Examples

### Allow alias with explicit credentials

The device must supply matching credentials to be permitted to register.

```json
{
  "status": "success",
  "result": {
    "username": "alice",
    "password": "password123"
  }
}
```

### Allow alias without authentication (not recommended)

Must include empty strings, not omit the fields:

```json
{
  "status": "success",
  "result": {
    "username": "",
    "password": ""
  }
}
```

### Reject an alias

```json
{
  "status": "success",
  "action": "reject",
  "result": {}
}
```

### Fall back to Pexip's local database

```json
{
  "status": "success",
  "action": "continue",
  "result": {}
}
```

---

## Implementation: LDAP-backed Registration

```python
@app.get("/policy/v1/registrations/{alias:path}")
async def registration_alias(alias: str, request: Request, _=Depends(check_auth)):
    params = request.query_params
    auth_type = params.get("auth_type", "credentials").strip('"')
    protocol = params.get("protocol", "")

    # Strip scheme if present
    if alias.startswith("sip:"):
        alias = alias[4:]

    log.info("↓ registration alias=%s auth=%s proto=%s",
             alias, auth_type, protocol)

    # For SSO registrations, just allow and let Pexip handle it
    if auth_type == "sso":
        return JSONResponse({
            "status": "success",
            "action": "continue",
            "result": {}
        })

    # Look up in LDAP
    user = await ldap_lookup(alias)
    if user is None:
        log.warning("DENY registration for unknown alias %s", alias)
        return JSONResponse({
            "status": "success",
            "action": "reject",
            "result": {}
        })

    return JSONResponse({
        "status": "success",
        "action": "continue",
        "result": {
            "username": user.username,
            "password": user.registration_password
        }
    })
```

---

## Security Notes

- **HTTPS is mandatory in production.** Passwords are sent in the clear in the response body.
- **Rotate passwords aggressively** — these are device registration secrets, not user passwords. Compromise of the policy server should not let an attacker permanently register devices.
- **Rate-limit unknown aliases** in your policy server to defend against alias enumeration / brute-force attacks.
- **Log every registration request** with IP, alias, and decision for audit.

---

## Test with curl

Pexip uses HTTP GET with Basic Auth. The alias goes in the URL path, not the query string. Exercise the credentials path, the SSO path, and the reject path separately:

```bash
# Known alias, credentials auth — should return username/password
curl -u user:pass "http://localhost:8080/policy/v1/registrations/alice@example.com\
?protocol=webrtc\
&auth_type=credentials\
&location=London\
&node_ip=10.44.155.21\
&remote_address=10.44.151.5\
&pseudo_version_id=77683.0.0\
&version_id=39"

# SSO registration — server should allow without credentials
curl -u user:pass "http://localhost:8080/policy/v1/registrations/alice@example.com\
?protocol=webrtc\
&auth_type=sso\
&location=London\
&node_ip=10.44.155.21\
&remote_address=10.44.151.5\
&pseudo_version_id=77683.0.0\
&version_id=39"

# Unknown alias — should reject
curl -u user:pass "http://localhost:8080/policy/v1/registrations/nobody@example.com\
?protocol=webrtc\
&auth_type=credentials\
&location=London\
&node_ip=10.44.155.21\
&remote_address=10.44.151.5\
&pseudo_version_id=77683.0.0\
&version_id=39"
```

A valid response should be `200 OK` with `Content-Type: application/json` and a body that includes `"status": "success"`.

Quick sanity checks to script against:

- `jq -e '.status == "success"'`
- Allow path: `jq -e '.action != "reject" and (.result.username | type == "string") and (.result.password | type == "string")'`
- Reject path: `jq -e '.action == "reject"'`
- SSO path: `jq -e '.action != "reject" and .result == {}'` (empty result expected for SSO)
- Confirm the response is sent over **HTTPS** in any non-dev environment — the password is in clear text in the body
