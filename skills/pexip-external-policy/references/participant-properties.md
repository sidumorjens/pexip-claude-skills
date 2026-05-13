# Participant Properties — Full Field Reference

**Request URI:** `GET /policy/v1/participant/properties`

Allows some of the participant's call properties (display name, role, audio mix, etc.) to be changed
before they join the conference. Use cases include anonymizing display names, modifying role based on
IdP attributes, and rejecting participants who don't meet ABAC criteria.

## Timing

- **WebRTC participants:** Applied **after** any PIN entry or SSO steps (so IdP attributes ARE available).
- **SIP/H.323 endpoints:** Applied **before** any PIN entry steps (so `preauthenticated_role` may be null).

Participant policy is applied **after** any service configuration policy, and **before** media location policy.

For WebRTC clients, Pexip typically sends **two participant_policy requests**: first with `participant_type=api`, then immediately after with `participant_type=standard`.

---

## Request Parameters

| Parameter | Description |
|---|---|
| `bandwidth` | The maximum requested bandwidth for the call (meaningful only for inbound). |
| `call_direction` | `"dial_in"`, `"dial_out"`, or `"non_dial"`. |
| `call_tag` | An optional call tag assigned to a participant. |
| `call_uuid` | A unique identifier for the participant's call. |
| `display_count` | Number of screens on the endpoint, if known. |
| `has_authenticated_display_name` | Boolean — IdP-authenticated display name. |
| `idp_attribute_<name>` | One query parameter per custom IdP attribute. E.g. an IdP attribute `locale` arrives as `idp_attribute_locale`. Configured under Users & Devices > Identity Providers > Advanced options. |
| `idp_uuid` | UUID of the IdP that authenticated the user. |
| `local_alias` | The incoming alias the endpoint dialed. |
| `location` | Pexip system location of the requesting Conferencing Node. |
| `ms-subnet` † | SIP subnet (SIP only). |
| `node_ip` | IP of the Conferencing Node. |
| `p_Asserted-Identity` † | Authenticated SIP identity (SIP only). |
| `participant_type` | `"standard"`, `"api"`, or `"api_host"`. |
| `participant_uuid` | UUID associated with the participant. |
| `preauthenticated_role` | Current role: `"guest"`, `"chair"`, or `null` (still at PIN entry or role not yet determined). |
| `previous_service_name` | Name of the previous service (prior to any transfer). |
| `protocol` | `"api"`, `"webrtc"`, `"sip"`, `"rtmp"`, `"h323"`, `"teams"`, `"mssip"`. |
| `pseudo_version_id` | Pexip build number. |
| `receive_from_audio_mix` | The audio mix the participant is receiving, e.g. `"main"`. |
| `registered` | Boolean — whether the participant is registered. |
| `remote_address` | IP of the participant. |
| `remote_alias` | Username or alias (may include scheme). |
| `remote_display_name` | Display name. |
| `remote_port` | IP port. |
| `send_to_audio_mixes_mix_name` | The audio mix name the participant is sending to. Currently always `main`. |
| `send_to_audio_mixes_prominent` | Whether the participant is "prominent" in the mix. Currently always `False`. |
| `service_name` | Service name (matches `name` from the prior service_configuration response). |
| `service_tag` | The service tag. |
| `supports_direct_media` | Boolean. |
| `teams_tenant_id` | MS Teams tenant ID. |
| `telehealth_request_id` ◊ | Epic telehealth call ID. |
| `trigger` | What triggered the request. |
| `unique_service_name` | Unique service identifier. |
| `vendor` | Endpoint system details. |
| `version_id` | Pexip version. |

> † Only on SIP-triggered requests when the SIP header is present.
> ◊ Only on Epic telehealth calls.

### Example GET request

```
GET /example.com/policy/v1/participant/properties
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
  &call_tag=
  &idp_uuid=
  &has_authenticated_display_name=False
  &supports_direct_media=False
  &teams_tenant_id=
  &location=London
  &node_ip=10.144.101.21
  &version_id=35
  &pseudo_version_id=77683.0.0
  &preauthenticated_role=chair
  &bypass_lock=False
  &receive_from_audio_mix=main
  &display_count=
  &participant_type=standard
  &participant_uuid=a13e1e71
  &local_alias=meet.bob
  &call_uuid=a13e1e71
  &breakout_uuid=
  &send_to_audio_mixes_mix_name=main
  &send_to_audio_mixes_prominent=False
  &unique_service_name=meet.bob
  &service_name=meet.bob
  &service_tag=
```

---

## Response Envelope

```json
{
  "status": "success",
  "action": "reject|continue",
  "result": { <participant_data> }
}
```

### `action` values for participant_properties

- **`"reject"`** — Pexip rejects the call. Optionally include a `reject_reason` in `result`.
- **`"continue"`** — Use the data in `result` to override participant properties.

> `action` is **ignored** if `status` is `"success"` and `result` contains valid data.

### All `result` fields are optional

You only include the properties you want to override.

| Field | Type | Default | Description |
|---|---|---|---|
| `bypass_lock` | Boolean | `false` | If `true`, this participant can enter a locked conference. |
| `call_tag` | String | — | Override for the call tag. |
| `can_receive_personal_mix` | Boolean | `false` | If `true`, the participant can use personal layouts. |
| `display_count` | Integer | — | Override for the number of screens on the endpoint. |
| `disable_overlay_text` | Boolean | `false` | If `true`, the participant's display name is not shown in the overlay. |
| `layout_group` | String | — | Layout group name (for participant pinning). |
| `preauthenticated_role` | String/null | — | `"chair"`, `"guest"`, or `null`. For SIP/H.323, returning `null` keeps the PIN-entry prompt; setting `"chair"`/`"guest"` is as if the user entered the matching PIN. |
| `prefers_multiscreen_mix` | Boolean | — | Override for multiscreen participant display. |
| `reject_reason` | String | — | Reason shown to the user when `action: "reject"`. |
| `remote_alias` | String | — | Override for the alias. Original is preserved in call logs. |
| `remote_display_name` | String/null | — | Override for the display name. Original is preserved in call logs. May be null if original was null. |
| `rx_presentation_policy` | String | `"ALLOW"` | `"ALLOW"` or `"DENY"` (UPPERCASE). Controls whether the participant can receive presentation content. |
| `spotlight` | Integer | — | Spotlight priority. Lower number = higher priority. Client API spotlights use current epoch time, so small integers (1, 2, 99) will outrank them. Can be cleared via client API. |
| `send_to_audio_mixes` | List | — | List of dictionaries, each with `mix_name` (string) and optionally `prominent` (boolean). |
| `receive_from_audio_mix` | String | — | The audio mix to receive from, e.g. `"main"`. |
| `wants_presentation_in_mix` | Boolean | — | Override for whether participant gets presentation in the layout mix. |

### `send_to_audio_mixes` shape

```json
"send_to_audio_mixes": [
  {"mix_name": "main",   "prominent": false},
  {"mix_name": "french", "prominent": true}
]
```

Hierarchical mix names use dot separators (e.g. `main.french` inherits from `main`). Max 3 levels of inheritance.

---

## Worked Examples

### Anonymize a witness and give them lock bypass

```json
{
  "status": "success",
  "action": "continue",
  "result": {
    "preauthenticated_role": "guest",
    "remote_alias": "Witness A alias",
    "remote_display_name": "Witness A",
    "bypass_lock": true
  }
}
```

### Reject for ABAC failure

```json
{
  "status": "success",
  "action": "reject",
  "result": {"reject_reason": "Insufficient clearance"}
}
```

### Force guest role for users without SSO

```json
{
  "status": "success",
  "action": "continue",
  "result": {
    "preauthenticated_role": "guest",
    "rx_presentation_policy": "DENY"
  }
}
```

### Translator: route into a language-specific audio mix

```json
{
  "status": "success",
  "action": "continue",
  "result": {
    "receive_from_audio_mix": "main.french",
    "send_to_audio_mixes": [
      {"mix_name": "main.french", "prominent": false}
    ]
  }
}
```

### Spotlight a VIP participant

```json
{
  "status": "success",
  "action": "continue",
  "result": {
    "spotlight": 1,
    "can_receive_personal_mix": true
  }
}
```

---

## Parsing `idp_attribute_*` parameters

```python
def extract_idp_attributes(query_params):
    """Each idp_attribute_<name> arrives as a query parameter; multi-valued attributes
    appear multiple times with the same key."""
    idp = {}
    for key in query_params.keys():
        if key.startswith("idp_attribute_"):
            name = key.removeprefix("idp_attribute_")
            idp[name] = query_params.getlist(key)
    return idp

# Usage in FastAPI
idp = extract_idp_attributes(request.query_params)
clearances = idp.get("clearance", [])      # e.g. ["SECRET"]
groups = idp.get("groups", [])             # e.g. ["analysts", "managers"]
```

---

## ABAC Decision Pattern

```python
@app.get("/policy/v1/participant/properties")
async def participant_properties(request: Request, _=Depends(check_auth)):
    params = request.query_params
    service_tag = params.get("service_tag", "")
    participant_uuid = params.get("participant_uuid", "")
    display_name = params.get("remote_display_name", "")
    protocol = params.get("protocol", "")

    idp = extract_idp_attributes(params)
    clearances = idp.get("clearance", [])

    log.info("↓ participant_policy uuid=%s name=%s tag=%s protocol=%s idp=%s",
             participant_uuid, display_name, service_tag, protocol, idp)

    # Look up classification of the VMR
    vmr_classification = VMR_CLASSIFICATIONS.get(service_tag)
    if not vmr_classification:
        # No classification → pass through unchanged
        return JSONResponse({"status": "success", "action": "continue", "result": {}})

    required = vmr_classification["min_clearance"]
    if required not in clearances:
        log.warning("DENY %s for %s (required %s, has %s)",
                    participant_uuid, display_name, required, clearances)
        return JSONResponse({
            "status": "success",
            "action": "reject",
            "result": {"reject_reason": f"Clearance {required} required"}
        })

    # Allow but downgrade to guest if not in admins list
    overrides = {}
    if "admins" not in idp.get("groups", []):
        overrides["preauthenticated_role"] = "guest"
        overrides["rx_presentation_policy"] = "DENY"

    return JSONResponse({
        "status": "success",
        "action": "continue",
        "result": overrides
    })
```

---

## Test with curl

Pexip uses HTTP GET with Basic Auth. Exercise your server end-to-end without Pexip — note `idp_attribute_*` parameters appear as individual query keys, and multi-valued attributes repeat the key:

```bash
curl -u user:pass "http://localhost:8080/policy/v1/participant/properties\
?call_direction=dial_in\
&protocol=webrtc\
&bandwidth=0\
&registered=False\
&trigger=web\
&remote_display_name=Alice\
&remote_alias=alice@example.com\
&remote_address=10.44.151.5\
&remote_port=58435\
&idp_uuid=00000000-0000-0000-0000-000000000001\
&has_authenticated_display_name=True\
&supports_direct_media=False\
&teams_tenant_id=\
&location=London\
&node_ip=10.144.101.21\
&version_id=39\
&pseudo_version_id=77683.0.0\
&preauthenticated_role=chair\
&participant_type=standard\
&participant_uuid=a13e1e71-0000-0000-0000-000000000001\
&call_uuid=a13e1e71-0000-0000-0000-000000000001\
&local_alias=meet.bob\
&unique_service_name=meet.bob\
&service_name=meet.bob\
&service_tag=meet.bob.tag\
&receive_from_audio_mix=main\
&send_to_audio_mixes_mix_name=main\
&send_to_audio_mixes_prominent=False\
&idp_attribute_clearance=SECRET\
&idp_attribute_groups=analysts\
&idp_attribute_groups=managers"
```

A valid response should be `200 OK` with `Content-Type: application/json` and a body that includes `"status": "success"`.

Quick sanity checks to script against:

- `jq -e '.status == "success"'`
- For an ABAC-allow path: `jq -e '.action != "reject"'` and inspect `.result` for expected overrides (e.g. `preauthenticated_role`, `rx_presentation_policy`)
- For an ABAC-deny path: `jq -e '.action == "reject" and (.result.reject_reason | type == "string")'`
- Drop or change `idp_attribute_clearance` to verify your deny branch fires
