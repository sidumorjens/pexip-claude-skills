# Media Location — Full Field Reference

**Request URI:** `GET /policy/v1/participant/location`

Determines which Pexip Infinity **system location** handles the call media for a participant. A Conferencing Node assigned to that location will be selected to handle media. Typically fires after `service_configuration` and `participant_properties`.

---

## Request Parameters

| Parameter | Description |
|---|---|
| `bandwidth` | Maximum requested bandwidth for the call. |
| `call_direction` | `"dial_in"`, `"dial_out"`, or `"non_dial"`. |
| `call_tag` | An optional call tag. |
| `has_authenticated_display_name` | Boolean. |
| `idp_uuid` | UUID of the IdP. |
| `local_alias` | The originally-dialed incoming alias for the associated service. |
| `location` | Pexip system location of the Conferencing Node making the request. |
| `ms-subnet` † | SIP only. |
| `node_ip` | IP of the Conferencing Node. |
| `p_Asserted-Identity` † | SIP only. |
| `previous_service_name` | Previous service (before any transfer). |
| `protocol` | `"api"`, `"webrtc"`, `"sip"`, `"rtmp"`, `"h323"`, `"teams"`, `"mssip"`. |
| `proxy_node_address` | Address of the Proxying Edge Node, if applicable. |
| `proxy_node_location` | Location of the Proxying Edge Node, if applicable. |
| `pseudo_version_id` | Pexip build number. |
| `registered` | Boolean. |
| `remote_address` | IP of the participant. |
| `remote_alias` | Participant alias. |
| `remote_display_name` | Display name. |
| `remote_port` | IP port. |
| `service_name` | Service name (matches `name` from the prior service_configuration response). |
| `service_tag` | Service tag. |
| `supports_direct_media` | Boolean. |
| `teams_tenant_id` | Teams tenant ID. |
| `telehealth_request_id` ◊ | Epic telehealth call ID. |
| `trigger` | Trigger for the policy request. |
| `unique_service_name` | Unique service identifier. |
| `vendor` | System details. |
| `version_id` | Pexip version. |

> † Only on SIP-triggered requests with the relevant SIP header.
> ◊ Only on Epic telehealth calls.

### Example GET request

```
GET /example.com/policy/v1/participant/location
  ?call_direction=dial_in
  &protocol=sip
  &bandwidth=0
  &vendor=Cisco/CE
  &encryption=On
  &registered=False
  &trigger=invite
  &remote_display_name=Alice
  &remote_alias=sip:alice@example.com
  &remote_address=10.44.151.5
  &remote_port=64410
  &proxy_node_address=
  &proxy_node_location=
  &call_tag=
  &idp_uuid=
  &has_authenticated_display_name=False
  &supports_direct_media=False
  &teams_tenant_id=
  &location=London
  &node_ip=10.144.101.21
  &version_id=35
  &pseudo_version_id=77683.0.0
  &unique_service_name=meet.bob
  &service_name=meet.bob
  &service_tag=
  &local_alias=meet.bob
  &request_id=644d4edc
```

---

## Response Envelope

```json
{
  "status": "success",
  "result": { <location_data> }
}
```

> Note: media_location has **no `action` field** — it's used purely to provide location data, not to control routing decisions.

### `result` fields

| Field | Required | Type | Description |
|---|---|---|---|
| `location` | Yes | String | Name of the principal location to use for media allocation. Must match an existing Pexip system location. |
| `overflow_locations` | No | List | Ordered list of location names to fall back to if the principal hits capacity. Once set by external policy, these cannot be modified by local policy. |

> **Critical:** Every name in `location` and `overflow_locations` **must** match a configured Pexip system location. If any name is invalid, the **entire response is deemed to have failed** and Pexip falls back to its own default behaviour.

### When Pexip uses an overflow location

`overflow_locations` is consulted at **call-setup time** when the principal location can't accept the new call. Pexip walks the list in order and places the call in the first location with available capacity.

What this means in practice:

- **Per-call decision.** Each call independently evaluates the list at setup. Two participants in the same conference can land in different locations.
- **Setup-time only.** Overflow isn't re-evaluated mid-call — once a call is placed, it stays in that location until it ends.
- **Order matters.** First entry with capacity wins. Put your preferred fallbacks first.
- **Once set, immutable for the call.** An external-policy-supplied `overflow_locations` list cannot be modified by local policy. Pick the right list at setup.

> The exact capacity trigger (which threshold, behaviour when all listed locations are full, interaction with cluster-wide location priority) is documented in the Pexip admin guide under media routing and capacity planning. Operators relying on `overflow_locations` as a load-balancing mechanism should understand their location's port allocations and configured limits before deploying.

---

## Worked Examples

### Use Oslo, overflow to London → Paris → New York

```json
{
  "status": "success",
  "result": {
    "location": "Oslo",
    "overflow_locations": ["London", "Paris", "New York"]
  }
}
```

### Stick with the requesting node's own location

```python
@app.get("/policy/v1/participant/location")
async def media_location(request: Request, _=Depends(check_auth)):
    return JSONResponse({
        "status": "success",
        "result": {"location": request.query_params.get("location")}
    })
```

### Geo-routing by participant IP

```python
@app.get("/policy/v1/participant/location")
async def media_location(request: Request, _=Depends(check_auth)):
    remote_ip = request.query_params.get("remote_address", "")
    location, overflow = geo_lookup(remote_ip)  # your function
    return JSONResponse({
        "status": "success",
        "result": {
            "location": location,
            "overflow_locations": overflow
        }
    })
```

### Fall back to Pexip default (no response data)

Either return HTTP 404, or:

```json
{
  "status": "success",
  "result": {}
}
```

Note: an empty `result` may be treated as invalid by some Pexip versions; preferring 404 is safer if you want explicit fallback.

---

## Test with curl

Pexip uses HTTP GET with Basic Auth for every request type. You can exercise your server end-to-end without Pexip:

```bash
curl -u user:pass "http://localhost:8080/policy/v1/participant/location\
?call_direction=dial_in\
&protocol=webrtc\
&bandwidth=0\
&registered=False\
&trigger=web\
&remote_display_name=Alice\
&remote_alias=alice@example.com\
&remote_address=10.44.151.5\
&remote_port=58435\
&proxy_node_address=\
&proxy_node_location=\
&call_tag=\
&idp_uuid=\
&has_authenticated_display_name=False\
&supports_direct_media=False\
&teams_tenant_id=\
&location=London\
&node_ip=10.144.101.21\
&version_id=39\
&pseudo_version_id=77683.0.0\
&unique_service_name=meet.bob\
&service_name=meet.bob\
&service_tag=\
&local_alias=meet.bob"
```

A valid response should be `200 OK` with `Content-Type: application/json` and a body that includes `"status": "success"` and a `result.location` matching a configured Pexip system location.

Quick sanity checks to script against:

- `jq -e '.status == "success"'` — the single most important field
- `jq -e '.result.location | type == "string" and length > 0'` — principal location is set
- `jq -e '.result.overflow_locations | type == "array"'` — overflow is a list (if returned)
