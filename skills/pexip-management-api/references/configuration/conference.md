# Virtual Meeting Room

**Endpoint:** `/api/admin/configuration/v1/conference/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `aliases` | `conference_alias` (related resource) | The aliases associated with this conference. |
| `allow_guests` | boolean | Whether Guest participants are allowed to join the conference. true: the conference will have two types of participants: Hosts and Guests. You must enter a PIN to be used by the Hosts. You can optionally enter a Guest PIN; if you do not enter a Guest PIN, Guests can join without a PIN, but the meeting will not start until the first Host has joined. false: all participants will have Host privileges. |
| `automatic_participants` | `automatic_participant` (related resource) | When a conference begins, a call will be placed automatically to these selected participants. |
| `breakout_rooms` | boolean | Allow this service to use different breakout rooms for participants. |
| `call_type` | string | Maximum media content of the conference. Participants will not be able to escalate beyond the selected capability. |
| `creation_time` | datetime | The time at which the configuration was created. |
| `crypto_mode` | string | Controls the media encryption requirements for participants connecting to this service. Use global setting: Use the global media encryption setting (Platform > Global Settings). Required: All participants (including RTMP participants) must use media encryption. Best effort: Each participant will use media encryption if their device supports it, otherwise the connection will be unencrypted. No encryption: All H.323, SIP and MS-SIP participants must use unencrypted media. (RTMP participants will use encryption if their device supports it, otherwise the connection will be unencrypted.) |
| `denoise_enabled` | boolean | If enabled, all noisy participants will have noise removed from speech. |
| `description` | string | A description of the service. Maximum length: 250 characters. |
| `direct_media` | string | Allows this VMR to use direct media between participants. When enabled, the VMR provides non-transcoded, encrypted, point-to-point calls between any two WebRTC participants. |
| `direct_media_notification_duration` | integer | The number of seconds to show a notification before being escalated into a transcoded call, or de-escalated into a direct media call. Range: 0s to 30s. Default: 0s. |
| `enable_active_speaker_indication` | boolean | Speaker display name or alias is shown across the bottom of their video image. |
| `enable_chat` | string | Enables relay of chat messages between conference participants using supported clients such as the Pexip apps. You can use this option to override the global configuration setting. |
| `enable_overlay_text` | boolean | If enabled, the display name or alias will be shown for each participant. |
| `force_presenter_into_main` | boolean | If enabled, a Host sending a presentation stream will always hold the main video position, instead of being voice-switched. |
| `gms_access_token` | `gms_access_token` (related resource) | Select an access token to use to resolve Google Meet meeting codes. |
| `guest_identity_provider_group` | `identity_provider_group` (related resource) | Select the set of Identity Providers to be offered to Guests to authenticate with, in order to join the conference. If this is blank, Guests will not be required to authenticate. |
| `guest_pin` | string | This optional field allows you to set a secure access code for Guest participants who dial in to the service. Length: 4-20 digits, including any terminal #. |
| `guest_view` | string | The layout that Guests will see. Guests only see Host participants. one_main_zero_pips: full-screen main speaker only. one_main_seven_pips: large main speaker and up to 7 other participants. one_main_twentyone_pips: main speaker and up to 21 other participants. two_mains_twentyone_pips: two main speakers and up to 21 other participants. four_mains_zero_pips: up to four main speakers, in a 2x2 layout. nine_mains_zero_pips: up to nine main speakers, in a 3x3 layout. sixteen_mains_zero_pips: up to sixteen main speakers, in a 4x4 layout. twentyfive_mains_zero_pips: up to twenty five main speakers, in a 5x5 layout. five_mains_seven_pips: Adaptive Composition layout (does not apply to service_type of 'lecture'). |
| `guests_can_present` | boolean | If enabled, Guests and Hosts can present into the conference. If disabled, only Hosts can present. |
| `guests_can_see_guests` | string | If enabled, when the Host leaves the conference Guests will see other Guests. If disabled, Guests will see a splash screen. |
| `host_identity_provider_group` | `identity_provider_group` (related resource) | Select the set of Identity Providers to be offered to Hosts to authenticate with, in order to join the conference. If this is blank, Hosts will not be required to authenticate. |
| `host_view` | string | The layout that Hosts will see. one_main_zero_pips: full-screen main speaker only. one_main_seven_pips: large main speaker and up to 7 other participants. one_main_twentyone_pips: main speaker and up to 21 other participants. two_mains_twentyone_pips: two main speakers and up to 21 other participants. four_mains_zero_pips: up to four main speakers in a 2x2 layout. nine_mains_zero_pips: up to nine main speakers, in a 3x3 layout. sixteen_mains_zero_pips: up to sixteen main speakers, in a 4x4 layout. twentyfive_mains_zero_pips: up to twenty five main speakers, in a 5x5 layout. five_mains_seven_pips: Adaptive Composition layout (does not apply to service_type of 'lecture'). |
| `id` | integer | The primary key. |
| `ivr_theme` | `ivr_theme` (related resource) | The theme for use with this service. |
| `live_captions_enabled` | string | Select whether to enable, disable, or use the default global live captions setting for this service. |
| `match_string` | string | An optional regular expression used to match against the alias entered by the caller into the Virtual Reception. If the entered alias does not match the expression, the Virtual Reception will not route the call. If this field is left blank, any entered alias is permitted. Maximum length: 250 characters. |
| `max_callrate_in` | integer | This optional field allows you to limit the bandwidth of media being received by Pexip Infinity from each individual participant dialed in to this service. Range: 128 to 8192. |
| `max_callrate_out` | integer | This optional field allows you to limit the bandwidth of media being sent by Pexip Infinity to each individual participant dialed in to this service. Range: 128 to 8192. |
| `max_pixels_per_second` | string | Sets the maximum call quality for each participant. |
| `media_playlist` | `media_library_playlist` (related resource) | The playlist to run when this Media Playback Service is used. |
| `mssip_proxy` | `mssip_proxy` (related resource) | The Skype for Business server to use to resolve the Skype for Business Conference ID entered by the user. You must then ensure that your Call Routing Rule that routes calls to your Skype for Business environment has Match against full alias URI selected and a Destination alias regex match in the style .+@example.com. |
| `mute_all_guests` | boolean | If enabled, all Guest participants will be muted by default. |
| `name` | string | The name used to refer to this service. Maximum length: 250 characters. |
| `non_idp_participants` | string | Determines whether participants attempting to join from devices other than Pexip apps (for example, SIP or H.323 endpoints) are permitted to join the conference when authentication is required. Disallow all: these devices may not join the conference. Allow if trusted: these devices may join the conference if they are locally registered. |
| `on_completion` | string | JSON format is used to specify what happens when the playlist finishes. If omitted, the last video's final frame remains in view. You can use one of the following options:{"disconnect": true} disconnects the user. {"transfer": {"conference": "<alias>", "role": "<role>"} } transfers the user to the specified alias, for example, a VMR. Role is optional and can be auto, host, or guest. If omitted, the default is auto. |
| `participant_limit` | integer | This optional field allows you to limit the number of participants allowed to join this Virtual Meeting Room. Range: 0 to 1000000. |
| `pin` | string | This optional field allows you to set a secure access code for participants who dial in to the service. Length: 4-20 digits, including any terminal #. |
| `pinning_config` | string | The layout pinning configuration that will be used for this conference. |
| `post_match_string` | string | An optional regular expression used to match against the meeting code, after the service lookup has been performed. Maximum length: 250 characters. |
| `post_replace_string` | string | An optional regular expression used to transform the meeting code so that, for example, it will match a Call Routing Rule for onward routing to the required conference. (Only applies if a Post-lookup regex match is also configured and the meeting code matches that regex.) Maximum length: 250 characters. |
| `primary_owner_email_address` | string | The email address of the owner of the VMR. Maximum length: 100 characters. |
| `replace_string` | string | An optional regular expression used to transform the alias entered by the caller into the Virtual Reception. (Only applies if a regex match string is also configured and the entered alias matches that regex.) Leave this field blank if you do not want to change the alias entered by the caller. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `scheduled_conferences` | `scheduled_conference` (related resource) | The scheduled conferences associated with this conference. |
| `scheduled_conferences_count` | integer | The number of scheduled conferences associated with this conference. |
| `service_type` | string | The type of conferencing service. conference: A Virtual Meeting Room. lecture: A Virtual Auditorium. two_stage_dialing: A Virtual Reception. |
| `softmute_enabled` | boolean | If enabled, noisy participants will have reduced volume until starting to speak. |
| `sync_tag` | string | A read-only identifier used by the system to track synchronization of this Virtual Meeting Room with LDAP. Maximum length: 250 characters. |
| `system_location` | `system_location` (related resource) | If selected, a Conferencing Node in this system location will perform the Skype for Business Conference ID lookup on the Skype for Business server. If a location is not selected, the IVR ingress node will perform the lookup. |
| `tag` | string | A unique identifier used to track usage of this service. Maximum length: 250 characters. |
| `teams_proxy` | `teams_proxy` (related resource) | The Teams Connector to use to resolve the Conference ID entered by the user. |
| `two_stage_dial_type` | string | The type of this Virtual Reception. Select Skype for Business if this Virtual Reception is to act as an IVR gateway to scheduled and ad hoc Skype for Business meetings. Select Google Meet if this Virtual Reception is to act as an IVR gateway to Google Meet meetings. Skype for Business meetings. Otherwise, select Regular. |
