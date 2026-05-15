# /api/admin/command/v1/participant/dial/

**Endpoint:** `/api/admin/command/v1/participant/dial/`

## Allowed methods

- **Allowed Methods (list):** POST

## Fields

| Field | Type | Description |
|---|---|---|
| `call_type` | string | Maximum media content of the call - does not apply to RTMP participants. The participant being called will not be able to escalate beyond the selected capability. audio: audio-only call. video-only: main video only; no presentation. video: main video and presentation. Default: video. |
| `conference_alias` | string | Select one of the aliases for this Virtual Meeting Room. The participant will see the call as coming from the selected alias. Maximum length: 250 characters. |
| `custom_sip_headers` | string | Optional custom SIP headers for outbound call. |
| `destination` | string | The alias of the participant being dialed out to. Maximum length: 250 characters. |
| `dtmf_sequence` | string | The DTMF sequence to be transmitted after the call to the dialed participant starts. Insert a comma for a 2 second pause. Maximum length: 250 characters. |
| `keep_conference_alive` | string | Determines whether the conference will continue when all other participants have disconnected. Default: keep_conference_alive |
| `local_display_name` | string | The optional display name for this local conference, which will be sent to the destination. Maximum length: 250 characters. |
| `node` | string | The IPv4 address of the Conferencing Node to dial out from. This value is optional if the system location parameter is specified. Maximum length: 255 characters. |
| `presentation_url` | string | The optional RTMP URL for the second (presentation) stream. Maximum length: 250 characters. |
| `protocol` | string | The signaling protocol to be used when dialing the participant. Default: sip. |
| `remote_display_name` | string | The optional user-facing display name for this participant, which will be shown in the participant lists. Maximum length: 250 characters. |
| `role` | string | The level of privileges the participant will have in the conference. Default: guest. |
| `routing` | string | Route this call manually using the defaults for the specified location - or route this call automatically using Call Routing Rules. |
| `streaming` | boolean | Whether the participant being dialed out to is a streaming or recording device. Default: False. |
| `system_location` | string | The system location from which the call will be placed. This value is optional if the Conferencing Node parameter is specified. Maximum length: 250 characters. |
