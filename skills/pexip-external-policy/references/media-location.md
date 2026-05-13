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
