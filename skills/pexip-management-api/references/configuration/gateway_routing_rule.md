# Call Routing Rule

**Endpoint:** `/api/admin/configuration/v1/gateway_routing_rule/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `call_type` | string | Maximum media content of the call. The participant being called will not be able to escalate beyond the selected capability. |
| `called_device_type` | string | The device or system to which the call is routed. The options are: Registered device or external system: routes the call to a matching registered device if it is currently registered, otherwise attempts to route the call via an external system such as a SIP proxy, Skype for Business server, H.323 gatekeeper or other gateway/ITSP. Registered devices only: routes the call to a matching registered device only (providing it is currently registered). Skype for Business meeting direct (Conference ID in dialed alias): routes the call via a Skype for Business server to a Skype for Business meeting. Note that the destination alias must be transformed into just a Skype for Business Conference ID. Skype for Business clients, or meetings via a Virtual Reception: routes the call via a Skype for Business server either to a Skype for Business client, or - for calls that have come via a Virtual Reception - to a Skype for Business meeting. For Skype for Business meetings via Virtual Reception routing, ensure that Match against full alias URI is selected and that the Destination alias regex match ends with .*. Google Meet meeting: routes the call to a Google Meet meeting. Microsoft Teams meeting: routes the call to a Microsoft Teams meeting. Microsoft Teams Room: routes the call to a Microsoft Teams Room. Epic Telehealth meeting: routes the call to an Epic Telehealth meeting. |
| `creation_time` | datetime | The time at which the Call Routing Rule was created. |
| `crypto_mode` | string | Controls the media encryption requirements for participants connecting to this service. Use global setting: Use the global media encryption setting (Platform > Global Settings). Required: All participants (including RTMP participants) must use media encryption. Best effort: Each participant will use media encryption if their device supports it, otherwise the connection will be unencrypted. No encryption: All H.323, SIP and MS-SIP participants must use unencrypted media. (RTMP participants will use encryption if their device supports it, otherwise the connection will be unencrypted.) |
| `denoise_audio` | boolean | Whether to remove background noise from audio streams as they pass through the infrastructure. |
| `description` | string | A description of the Call Routing Rule. Maximum length: 250 characters. |
| `disabled_codecs` | `disabled_codec` (related resource) | Choose codecs to disable. |
| `enable` | boolean | Determines whether or not the rule is enabled. Any disabled rules still appear in the rules list but are ignored. Use this setting to test configuration changes, or to temporarily disable specific rules. |
| `external_participant_avatar_lookup` | string | Determines whether or not avatars for external participants will be retrieved using the method appropriate for the external meeting type. You can use this option to override the global configuration setting. |
| `gms_access_token` | `gms_access_token` (related resource) | The access token to use when resolving Google Meet meeting codes. |
| `h323_gatekeeper` | `h323_gatekeeper` (related resource) | When calling an external system, this is the H.323 gatekeeper to use for outbound H.323 calls. Select Use DNS to try to use normal H.323 resolution procedures to route the call. |
| `id` | integer | The primary key. |
| `ivr_theme` | `ivr_theme` (related resource) | The theme for use with this service. If no theme is selected here, files from the theme that has been selected as the default (Platform > Global settings > Default theme) will be applied. |
| `live_captions_enabled` | string | Select whether to enable, disable, or use the default global live captions setting for this service. |
| `match_incoming_calls` | boolean | Applies this rule to incoming calls that have not been routed to a Virtual Meeting Room or Virtual Reception, and should be routed via the Pexip Distributed Gateway service. |
| `match_incoming_h323` | boolean | Select whether this rule should apply to incoming H.323 calls. |
| `match_incoming_mssip` | boolean | Select whether this rule should apply to incoming Skype for Business (MS-SIP) calls. |
| `match_incoming_only_if_registered` | boolean | Only apply this rule to incoming calls from devices, videoconferencing endpoints, soft clients or Pexip apps that are registered to Pexip Infinity.  Note that the call must also match one of the selected protocols below. Calls placed from non-registered clients or devices, or from the Pexip web app will not be routed by this rule if it is enabled. |
| `match_incoming_sip` | boolean | Select whether this rule should apply to incoming SIP calls. |
| `match_incoming_teams` | boolean | Select whether this rule should apply to incoming Teams calls. |
| `match_incoming_webrtc` | boolean | Select whether this rule should apply to incoming calls from Pexip apps (WebRTC / RTMP). |
| `match_outgoing_calls` | boolean | Applies this rule to outgoing calls placed from a conference service (e.g. when adding a participant to a Virtual Meeting Room) where Automatic routing has been selected. |
| `match_source_location` | `system_location` (related resource) | Applies the rule only if the incoming call is being handled by a Conferencing Node in the selected location or the outgoing call is being initiated from the selected location. To apply the rule regardless of the location, select Any Location. |
| `match_string` | string | The regular expression that the destination alias (the alias that was dialed) is checked against to see if this rule applies to this call. Maximum length: 250 characters. |
| `match_string_full` | boolean | This setting is for advanced use cases and will not normally be required. By default, Pexip Infinity matches against a parsed version of the destination alias, i.e. it ignores the URI scheme, any other parameters, and any host IP addresses. So, if the original alias is "sip:alice@example.com;transport=tls" for example, then by default the rule will match against "alice@example.com". Select this option to match against the full, unparsed alias instead. |
| `max_callrate_in` | integer | This optional field allows you to limit the bandwidth of media being received by Pexip Infinity from each individual participant dialed in via this Call Routing Rule. Range: 128 to 8192. |
| `max_callrate_out` | integer | This optional field allows you to limit the bandwidth of media being sent by Pexip Infinity to each individual participant dialed out from this Call Routing Rule. Range: 128 to 8192. Default: 4128. |
| `max_pixels_per_second` | string | Sets the maximum call quality for each participant. |
| `mssip_proxy` | `mssip_proxy` (related resource) | When calling an external system, this is the Skype for Business server to use for outbound Skype for Business (MS-SIP) calls. Select Use DNS to try to use normal Skype for Business (MS-SIP) resolution procedures to route the call. When calling a Skype for Business meeting, this is the Skype for Business server to use for the Conference ID lookup and to place the call. |
| `name` | string | The name used to refer to this Call Routing Rule. Maximum length: 250 characters. |
| `outgoing_location` | `system_location` (related resource) | When calling an external system, this forces the outgoing call to be handled by a Conferencing Node in a specific location. When calling a Skype for Business meeting, a Conferencing Node in this location will handle the outgoing call, and - for 'Skype for Business meeting direct' targets - perform the Conference ID lookup on the Skype for Business server. Select Automatic to allow Pexip Infinity to automatically select which Conferencing Node to use. |
| `outgoing_protocol` | string | When calling an external system, this is the protocol to use when placing the outbound call. Note that if the call is to a registered device, Pexip Infinity will instead use the protocol that the device used to make the registration. |
| `priority` | integer | The priority of this rule. Rules are checked in ascending priority order until the first matching rule is found, and it is then applied. Range: 1 to 200. |
| `replace_string` | string | The regular expression string used to transform the originally dialed alias (if a match was found). Leave blank to leave the originally dialed alias unchanged. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `sip_proxy` | `sip_proxy` (related resource) | When calling an external system, this is the SIP proxy to use for outbound SIP calls. Select Use DNS to try to use normal SIP resolution procedures to route the call. |
| `stun_server` | `stun_server` (related resource) | The STUN server to be used for outbound Skype for Business (MS-SIP) calls (where applicable). |
| `tag` | string | A unique identifier used to track usage of this Call Routing Rule. Maximum length: 250 characters. |
| `teams_proxy` | `teams_proxy` (related resource) | The Teams Connector to use for the Teams meeting. If you do not specify anything, the Teams Connector associated with the outgoing location is used. |
| `telehealth_profile` | `telehealth_profile` (related resource) | The Telehealth Profile to use for the meeting. |
| `treat_as_trusted` | boolean | This indicates the target of this routing rule will treat the caller as part of the target organization for trust purposes. |
| `turn_server` | `turn_server` (related resource) | The TURN server to be used for outbound Skype for Business (MS-SIP) calls (where applicable). |
