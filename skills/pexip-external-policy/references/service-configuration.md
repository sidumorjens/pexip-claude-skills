# Service Configuration — Full Field Reference

**Request URI:** `GET /policy/v1/service/configuration`

Triggered when Pexip Infinity needs the configuration details of a service. This happens when:
- Pexip receives an incoming call request
- Pexip needs to place a call to a given alias (dial-out)

## Request Parameters

| Parameter | Description |
|---|---|
| `bandwidth` | The maximum requested bandwidth for the call. Present on both inbound and outbound, but meaningful only for inbound. |
| `breakout_uuid` | The UUID of a breakout room (if applicable). |
| `call_direction` | `"dial_in"`, `"dial_out"`, or `"non_dial"` (H.323 LRQ, SIP SUBSCRIBE/OPTIONS, etc). |
| `call_tag` | An optional call tag assigned to the participant. |
| `display_count` | Number of screens signaled by a Microsoft Teams Room when joining via One-Touch Join (only in service configuration). |
| `has_authenticated_display_name` | Boolean — whether the display name was provided and authenticated by an Identity Provider. |
| `idp_uuid` | UUID of the IdP that authenticated the participant's display name and provided idp_attributes. |
| `local_alias` | The incoming alias (typically the alias the endpoint dialed). The primary item used to determine the response. |
| `location` | The Pexip Infinity system location of the Conferencing Node making the request. |
| `ms-subnet` † | The sender's subnet address. (Only on SIP-triggered requests when SIP header is present.) |
| `node_ip` | The IP address of the Conferencing Node making the request. |
| `p_Asserted-Identity` † | The authenticated identity from the SIP message. (Only on SIP-triggered requests when SIP header is present.) |
| `previous_service_name` | The name of the previous service (prior to any call transfer). |
| `protocol` | `"api"`, `"webrtc"`, `"sip"`, `"rtmp"`, `"h323"`, `"teams"`, or `"mssip"`. (Pexip apps initially report `"api"`.) |
| `pseudo_version_id` | The Pexip Infinity software build number. |
| `registered` | Boolean — whether the remote participant is registered. |
| `remote_address` | IP address of the remote participant. |
| `remote_alias` | The user name or registered alias of the endpoint. May include scheme, e.g. `sip:alice@example.com`. |
| `remote_display_name` | Display name of the remote participant. |
| `remote_port` | IP port of the remote participant. |
| `service_name` ‡ | The service name (matches `name` returned from the original service config response). |
| `service_tag` †† | The service tag associated with `service_name`. |
| `supports_direct_media` | Boolean — whether the service supports direct media. |
| `teams_tenant_id` | Microsoft Teams tenant ID on an inbound Teams call (Teams Rooms SIP/H.323). |
| `telehealth_request_id` ◊ | Epic telehealth call ID. |
| `third_party_passcode` | Passcode field from MS Teams Room calendaring service (Cross-platform SIP join for Teams Rooms). |
| `trigger` | What triggered the policy request: `"web"`, `"web_avatar_fetch"`, `"invite"`, `"options"`, `"subscribe"`, `"setup"`, `"arq"`, `"lrq"`, `"two_stage_dialing"`, `"teams"`, or `"unspecified"`. |
| `unique_service_name` ‡ | Unique service identifier. For gateways: rule name + unique identifier. For breakouts: `<vmr>_breakout_<uuid>`. Otherwise same as `service_name`. |
| `vendor` | System details (manufacturer/version for hard endpoints; browser/OS for soft clients). |
| `version_id` | The Pexip Infinity software version number. |

> † Only included if request was triggered by a SIP message containing the header. In local policy these are referenced as `ms_subnet` and `p_asserted_identity` (underscore/lowercase). Values arrive as JSON lists.
> ‡ Only included in outbound call requests and for breakout rooms.
> †† Only included in outbound call requests.
> ◊ Only included in Epic telehealth calls.

### Example GET request

```
GET /example.com/policy/v1/service/configuration
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
  &remote_port=58435
  &call_tag=
  &idp_uuid=
  &has_authenticated_display_name=False
  &supports_direct_media=False
  &teams_tenant_id=
  &location=London
  &node_ip=10.144.101.21
  &version_id=35
  &pseudo_version_id=77683.0.0
  &local_alias=meet.bob
```

---

## Response Envelope

```json
{
  "status": "success",
  "action": "reject|redirect|continue",
  "result": { <service_configuration_data> }
}
```

### `action` values for service_configuration

- **`"reject"`** — Pexip rejects the call (returns "conference not found"). If local policy is also enabled, local policy can still provide a service configuration to override the reject.
- **`"redirect"`** — Pexip sends a SIP `302 Redirect` to the endpoint, telling it to call a different alias. The `result` must be `{"new_alias": "sip:alias@example.com"}`.
- **`"continue"`** — Falls back to Pexip's default behaviour (try to retrieve from internal database).

> The `action` field is **ignored if `status` is `"success"` and `result` contains valid data**. In that case, Pexip uses the supplied configuration.

### Per-participant variation

Each request for the same service should generally return the same configuration. The only fields that legitimately vary per participant are:

- `guest_identity_provider_group`
- `host_identity_provider_group`
- `pin`
- `guest_pin`
- `max_callrate_in`
- `max_callrate_out`

For other per-participant changes (display name, role overrides), use **participant policy** instead.

---

## Service Type: `"conference"` (VMR) / `"lecture"` (Virtual Auditorium)

### Required fields

| Field | Type | Description |
|---|---|---|
| `name` | String | The name of the service. Pexip uses this as `service_name` in subsequent requests. For breakout rooms, this is the **main VMR name**. |
| `service_tag` | String | Unique identifier used to track usage of this service. |
| `service_type` | String | Either `"conference"` (VMR) or `"lecture"` (Virtual Auditorium). |

### Optional fields

| Field | Type | Default | Description |
|---|---|---|---|
| `allow_guests` | Boolean | `false` | If `true`, distinguishes between Host and Guest participants (`pin` for Hosts; `guest_pin` optional). If `false`, all participants are Hosts. |
| `automatic_participants` | List | — | A list of participants to dial automatically when the conference starts. See ADP fields below. |
| `breakout_rooms` | Boolean | `false` | Whether breakout rooms are enabled for this conference. |
| `bypass_proxy` | Boolean | `false` | If `true`, on a Proxying Edge Node, the client is instructed to send media directly to the Transcoding Conferencing Node. |
| `call_type` | String | `"video"` | `"video"`, `"video-only"`, or `"audio"`. |
| `crypto_mode` | String | global | Media encryption: `null` (use global), `"besteffort"`, `"on"`, or `"off"`. |
| `description` | String | — | A description of the service. |
| `denoise_enabled` | Boolean | `false` | Technology-preview Denoise feature toggle. |
| `direct_media` | String | `"never"` | `"best_effort"`, `"always"`, or `"never"`. Not supported if breakout_rooms is enabled. |
| `direct_media_notification_duration` | Integer | `0` | Seconds to show notification before escalation. Range 0-30. |
| `enable_chat` | String | `"default"` | `"default"`, `"yes"`, or `"no"`. |
| `enable_active_speaker_indication` | Boolean | `false` | Show active speaker name across bottom of video. |
| `enable_overlay_text` | Boolean | `false` | Display name overlays for all participants. |
| `force_presenter_into_main` (lecture only) | Boolean | `false` | Lock presenting Host into main video position. |
| `guest_pin` | String | — | Guest PIN. |
| `guest_view` (lecture only) | String | `"one_main_seven_pips"` | The layout seen by Guests. See layout values below. |
| `guests_can_present` | Boolean | `true` | If `false`, only Hosts can present content. |
| `guests_can_see_guests` (lecture only) | String | `"no_hosts"` | `"no_hosts"`, `"always"`, or `"never"`. |
| `guest_identity_provider_group` | String | — | Set of IdPs offered to Guests for authentication. Blank = no authentication required. |
| `host_identity_provider_group` | String | — | Set of IdPs offered to Hosts. |
| `host_view` (lecture only) | String | `"one_main_seven_pips"` | The layout seen by Hosts. |
| `ivr_theme_name` | String | default | Theme name. |
| `live_captions_enabled` | String | `"default"` | `"default"`, `"yes"`, or `"no"`. |
| `live_captions_language` | String | — | Language for live captions. Must match `source_language` for AIMS v1.0. |
| `local_display_name` | String | — | Display name of the calling alias. |
| `locked` | Boolean | `false` | If `true`, conference is locked on creation. No effect on running conferences. |
| `max_callrate_in` | Integer | — | Max inbound bandwidth (bps), range 128000–8192000. |
| `max_callrate_out` | Integer | — | Max outbound bandwidth (bps), range 128000–8192000. |
| `max_pixels_per_second` | String | global | `null` (global), `"sd"`, `"hd"`, or `"fullhd"`. |
| `mute_all_guests` | Boolean | `false` | If `true`, mute Guests on join. |
| `non_idp_participants` | String | `"disallow_all"` | For SSO-protected services: `"disallow_all"` or `"allow_if_trusted"`. |
| `participant_limit` | Integer | — | Max participants allowed. |
| `pin` | String | — | Host PIN. |
| `pinning_config` | String | — | Name of the pinning configuration from the theme. |
| `prefer_ipv6` | String | `"default"` | `"default"`, `"yes"`, or `"no"`. |
| `primary_owner_email_address` | String | — | VMR owner's email. |
| `softmute_enabled` | Boolean | `false` | Technology-preview Softmute feature. |
| `source_language` | String | — | Audio stream language used by AIMS for live captions. |
| `view` (conference only) | String | `"one_main_seven_pips"` | Layout seen by all participants. |

### Layout values (`view`, `host_view`, `guest_view`)

`one_main_zero_pips`, `one_main_seven_pips`, `one_main_twentyone_pips`, `two_mains_twentyone_pips`,
`one_main_thirtythree_pips`, `four_mains_zero_pips`, `nine_mains_zero_pips`, `sixteen_mains_zero_pips`,
`twentyfive_mains_zero_pips`, `five_mains_seven_pips` (Adaptive Composition), `one_main_one_pip`,
`one_main_nine_around`, `one_main_twelve_around`, `two_mains_eight_around`, `teams` (Teams gateway only).

---

## Breakout Room Fields

When the service configuration represents a breakout room, add these fields alongside the conference fields:

| Field | Required | Type | Description |
|---|---|---|---|
| `breakout` | Yes | Boolean | `true` indicates this is a breakout. If `true`, `breakout_rooms` should be `false`. `name` must be the main VMR name. |
| `breakout_uuid` | Yes | String | UUID `XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX` identifying this breakout. |
| `breakout_name` | Yes | String | Display name of the breakout room. |
| `breakout_uuids` | No | List | When returning **main room** config to a Host, listing breakout UUIDs causes the Host to attempt joining each as a control-only participant. Each triggers another policy lookup with `service_name: "<main>_breakout_<uuid>"`. |
| `breakout_description` | No | String | Long name/description. |
| `breakout_guests_allowed_to_leave` | No | Boolean | If `true`, participants can leave and return to main room. Default `false`. |
| `end_action` | No | String | `"disconnect"` or `"transfer"` (back to main room) when timer expires. Default `"transfer"`. |
| `end_time` | No | Integer | Time when breakout ends (seconds since epoch). `0` = no automatic end. |

---

## Service Type: `"gateway"` (Infinity Gateway Call)

### Required fields

| Field | Type | Description |
|---|---|---|
| `local_alias` | String | The calling/"from" alias (the alias the recipient would use to call back). |
| `name` | String | Unique service name (ensure uniqueness across gateway calls). |
| `outgoing_protocol` | String | `"h323"`, `"sip"`, `"mssip"`, `"rtmp"`, `"gms"` (Google Meet), or `"teams"`. |
| `remote_alias` | String | Alias to call. Can include scheme; call uses `outgoing_protocol`. |
| `service_tag` | String | Unique identifier for tracking. |
| `service_type` | String | Must be `"gateway"`. |

### Optional fields

| Field | Type | Default | Description |
|---|---|---|---|
| `bypass_proxy` | Boolean | `false` | Same as conference. |
| `call_type` | String | `"video"` | `"video"`, `"video-only"`, `"audio"`, or `"auto"` (match inbound). |
| `crypto_mode` | String | global | Same as conference. |
| `called_device_type` | String | `"external"` | `"external"`, `"registration"`, `"mssip_conference_id"`, `"mssip_server"`, `"gms_conference"`, `"teams_conference"`, `"teams_user"`, `"telehealth_profile"`. |
| `denoise_audio` | Boolean | `true` | Google Meet only: remove background noise from audio. |
| `description` | String | — | Service description. |
| `dtmf_sequence` | String | — | DTMF to transmit after dialed call starts. |
| `enable_active_speaker_indication` | Boolean | `false` | |
| `enable_overlay_text` | Boolean | `false` | |
| `external_participant_avatar_lookup` | String | `"default"` | Microsoft Teams only. `"default"`, `"yes"`, `"no"`. |
| `gms_access_token_name` | String | — | Access token name to resolve Google Meet IDs. |
| `h323_gatekeeper_name` | String | — | Name of an H.323 gatekeeper configured in Pexip (DNS used otherwise). |
| `ivr_theme_name` | String | default | |
| `live_captions_enabled` | String | `"default"` | |
| `live_captions_language` | String | — | |
| `local_display_name` | String | — | |
| `max_callrate_in` | Integer | — | bps, 128000–8192000 |
| `max_callrate_out` | Integer | — | bps, 128000–8192000 |
| `max_pixels_per_second` | String | global | |
| `mssip_proxy_name` | String | — | Name of S4B server (DNS used otherwise). |
| `outgoing_location_name` | String | — | Conferencing Node location to place the call from. |
| `prefer_ipv6` | String | `"default"` | |
| `sip_proxy_name` | String | — | Name of a SIP proxy (DNS used otherwise). |
| `source_language` | String | — | |
| `stun_server_name` | String | — | STUN server for ICE-enabled SIP/WebRTC endpoints. |
| `teams_fit_to_frame` | String | `"no"` | Teams calls only. `"yes"` or `"no"`. |
| `teams_proxy_name` | String | — | Teams Connector to handle the call. |
| `transcoding_enabled` | Boolean | `true` | Tech preview. If `false`, SIP-to-SIP calls skip transcoding. |
| `treat_as_trusted` | Boolean | — | Treat caller as part of target organization for trust purposes. |
| `turn_server_name` | String | — | TURN server for ICE-enabled SIP/WebRTC endpoints. |
| `view` | String | `"one_main_seven_pips"` | Layout. |

> All `*_name` fields must match the name of the corresponding object configured in Pexip Infinity. Mismatches cause the entire response to be considered failed.

---

## Service Type: `"two_stage_dialing"` (Virtual Reception)

### Required fields

| Field | Type | Description |
|---|---|---|
| `name` | String | Service name. |
| `service_tag` | String | Unique tracking ID. |
| `service_type` | String | Must be `"two_stage_dialing"`. |

### Optional fields

| Field | Type | Default | Description |
|---|---|---|---|
| `bypass_proxy` | Boolean | `false` | |
| `call_type` | String | `"video"` | `"video"`, `"video-only"`, `"audio"`. |
| `crypto_mode` | String | global | |
| `description` | String | — | |
| `gms_access_token_name` | String | — | Access token (trusted or untrusted) for Google Meet ID resolution. |
| `ivr_theme_name` | String | default | |
| `local_display_name` | String | — | |
| `match_string` | String | — | Regex to match against the alias entered by the caller. Blank = any alias allowed. |
| `max_callrate_in` | Integer | — | bps, 128000–8192000 |
| `max_callrate_out` | Integer | — | bps, 128000–8192000 |
| `max_pixels_per_second` | String | global | |
| `mssip_proxy_name` | String | — | S4B server for SfB Conference ID resolution. |
| `post_match_string` | String | — | Regex to match the meeting code. Often used with `post_replace_string`. |
| `post_replace_string` | String | — | Transforms the meeting code into an alias pattern. |
| `replace_string` | String | — | Regex transform of the entered alias (if `match_string` matches). |
| `system_location_name` | String | — | Location used for SfB/Teams/Meet lookups (when `two_stage_dial_type` ≠ `"regular"`). |
| `teams_proxy_name` | String | — | Teams Connector for Teams meeting code resolution. |
| `two_stage_dial_type` | String | `"regular"` | `"regular"`, `"mssip"`, `"gms"`, `"teams"`. |

---

## Service Type: `"media_playback"` (Media Playback Service)

### Required fields

| Field | Type | Description |
|---|---|---|
| `name` | String | |
| `media_playlist_name` | String | The name of the configured playlist. |
| `service_type` | String | Must be `"media_playback"`. |
| `service_tag` | String | |

### Optional fields

| Field | Type | Default | Description |
|---|---|---|---|
| `allow_guests` | Boolean | `false` | |
| `description` | String | — | |
| `guest_pin` | String | — | |
| `guest_identity_provider_group` | String | — | |
| `host_identity_provider_group` | String | — | |
| `ivr_theme_name` | String | default | |
| `max_callrate_in` | Integer | — | |
| `max_callrate_out` | Integer | — | |
| `max_pixels_per_second` | String | global | |
| `non_idp_participants` | String | `"disallow_all"` | |
| `on_completion` | Object | — | Action on playlist completion. See below. |
| `pin` | String | — | |

### `on_completion` shape

```json
"on_completion": {"disconnect": true}
```

or

```json
"on_completion": {"transfer": {"conference": "<alias>"}}
```

or with role:

```json
"on_completion": {"transfer": {"conference": "<alias>", "role": "chair|guest"}}
```

---

## Service Type: `"test_call"` (Test Call Service)

### Required fields

| Field | Type | Description |
|---|---|---|
| `name` | String | |
| `service_tag` | String | |
| `service_type` | String | Must be `"test_call"`. |

### Optional fields

| Field | Type | Default | Description |
|---|---|---|---|
| `bypass_proxy` | Boolean | `false` | |
| `call_type` | String | `"video"` | |
| `crypto_mode` | String | global | |
| `description` | String | — | |
| `ivr_theme_name` | String | default | |
| `local_display_name` | String | — | |
| `max_callrate_in` | Integer | — | |
| `max_pixels_per_second` | String | global | |

---

## Automatically Dialed Participants (ADP) Fields

The `automatic_participants` list (in conference/lecture responses) contains objects with these fields:

| Field | Required | Type | Description |
|---|---|---|---|
| `local_alias` | Yes | String | Calling/"from" alias the recipient would use to call back. |
| `protocol` | Yes | String | `"h323"`, `"sip"`, `"mssip"`, `"rtmp"`. |
| `remote_alias` | Yes | String | Alias of the endpoint to call. |
| `role` | Yes | String | `"chair"` or `"guest"`. |
| `call_type` | No | String | `"video"`, `"video-only"`, `"audio"`. Default `"video"`. |
| `dtmf_sequence` | No | String | DTMF to transmit after the call starts. |
| `keep_conference_alive` | No | String | `"keep_conference_alive"`, `"keep_conference_alive_if_multiple"` (default), `"keep_conference_alive_never"`. |
| `local_display_name` | No | String | Display name of the calling alias. |
| `presentation_url` | No | String | For RTMP: separate destination for presentation stream. |
| `remote_display_name` | No | String | Friendly name for this participant. |
| `routing` | No | String | `"manual"` (default) or `"routing_rule"`. |
| `streaming` | No | Boolean | `true` = streaming/recording device. Default `false`. |
| `system_location_name` | No | String | Conferencing Node location to place the call from. |

---

## Worked Examples

### Conference with two automatic dial-outs

```json
{
  "status": "success",
  "action": "continue",
  "result": {
    "service_type": "conference",
    "name": "Alice Jones",
    "service_tag": "abcd1234",
    "description": "Alice Jones personal VMR",
    "pin": "123456",
    "allow_guests": true,
    "guest_pin": "567890",
    "view": "one_main_zero_pips",
    "enable_overlay_text": true,
    "automatic_participants": [
      {
        "remote_alias": "sip:alice@example.com",
        "remote_display_name": "Alice",
        "local_alias": "meet.alice@example.com",
        "local_display_name": "Alice's VMR",
        "protocol": "sip",
        "role": "chair",
        "system_location_name": "London"
      },
      {
        "remote_alias": "rtmp://example.com/live/alice_vmr",
        "local_alias": "meet.alice@example.com",
        "local_display_name": "Alice's VMR",
        "protocol": "rtmp",
        "role": "guest",
        "streaming": true
      }
    ]
  },
  "xyz_version": "1.2"
}
```

### Reject

```json
{
  "status": "success",
  "action": "reject"
}
```

### Redirect (SIP 302)

```json
{
  "status": "success",
  "action": "redirect",
  "result": {"new_alias": "sip:bob.alternate@example.com"}
}
```

### Gateway call to Teams

```json
{
  "status": "success",
  "action": "continue",
  "result": {
    "service_type": "gateway",
    "name": "teams-bridge-001",
    "service_tag": "teams-gw",
    "local_alias": "meet@example.com",
    "remote_alias": "19:meeting_xyz@thread.v2",
    "outgoing_protocol": "teams",
    "called_device_type": "teams_conference",
    "teams_proxy_name": "TeamsConnectorUS",
    "call_type": "video",
    "treat_as_trusted": true
  }
}
```

### Breakout room (waiting room pattern)

```json
{
  "status": "success",
  "action": "continue",
  "result": {
    "name": "main-vmr",
    "service_type": "conference",
    "service_tag": "lobby_alice",
    "breakout": true,
    "breakout_uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "breakout_name": "Waiting Room - Alice",
    "breakout_description": "Please wait to be admitted",
    "end_action": "transfer",
    "end_time": 0,
    "allow_guests": true,
    "pin": ""
  }
}
```

### Virtual Reception routing to Google Meet

```json
{
  "status": "success",
  "action": "continue",
  "result": {
    "service_type": "two_stage_dialing",
    "name": "gmeet-reception",
    "service_tag": "vr-gmeet",
    "two_stage_dial_type": "gms",
    "gms_access_token_name": "MeetTokenUntrusted",
    "match_string": "^[a-z]{3}-[a-z]{4}-[a-z]{3}$",
    "system_location_name": "Sydney"
  }
}
```

---

## Dial-out Restrictions

When `call_direction=dial_out`, the response **must match the existing service data** (same `name`, `service_type`, etc.). The only fields you can meaningfully control on dial-out are:

- `prefer_ipv6` in the service_configuration response
- The media location (via the subsequent media_location request)
