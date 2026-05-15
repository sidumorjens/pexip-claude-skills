# Participant

**Endpoint:** `/api/admin/history/v1/participant/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `av_id` | string | The ID of the audio/video participant. |
| `bandwidth` | integer | The maximum bandwidth (in kbps) available for the call. |
| `call_direction` | string | The direction of the call. |
| `call_quality` | string | The overall quality of the call based on packet loss. |
| `call_tag` | string | Optional client-supplied identifier for this call. Maximum length: 1000 characters. |
| `call_uuid` | string | The unique identifier of the participant call. Maximum length: 200 characters. |
| `conference` | `conference` (related resource) | A single related resource. Can be either a URI or set of nested resource data. |
| `conference_name` | string | The name used to refer to the service. Maximum length: 250 characters. |
| `conversation_id` | string | A unique identifier to correlate multiple related calls. |
| `disconnect_reason` | string | The reason the participant was disconnected. Maximum length: 250 characters. |
| `display_name` | string | The display name of the participant. Maximum length: 1000 characters. |
| `duration` | integer | The duration of the call in seconds. |
| `encryption` | string | The media encryption status for the call. |
| `end_time` | datetime | The time at which the participant disconnected. |
| `has_media` | boolean | Whether the participant transmitted or received media streams. |
| `id` | string | The primary key. |
| `idp_uuid` | string | Indicates the Identity Provider that authenticated the participant. |
| `is_direct` | boolean | Indicates whether this participant's media went direct. |
| `is_idp_authenticated` | boolean | Indicates whether the participant was authenticated by an Identity Provider. |
| `is_streaming` | boolean | Indicates whether the participant was a streaming or recording device. |
| `license_count` | integer | The number of licenses consumed by the participant. |
| `license_type` | string | The number of licenses consumed by the participant. |
| `local_alias` | string | The alias of the conference. Maximum length: 1000 characters. |
| `media_node` | string | The Conferencing Node the participant was connected to for call media. Maximum length: 50 characters. |
| `media_streams` | `media_stream` (related resource) | The media streams created by the participant. |
| `parent_id` | string | This field is deprecated and will be ignored. |
| `presentation_id` | string | The ID of the presentation participant. |
| `protocol` | string | The signaling protocol for the call. |
| `proxy_node` | string | The Proxying Edge Node that was proxying media for the participant. Maximum length: 50 characters. |
| `remote_address` | string | The remote IP address used for signaling. Maximum length: 50 characters. |
| `remote_alias` | string | The alias of the participant. Maximum length: 1000 characters. |
| `remote_port` | integer | The IP port used for signaling. Range: 0 to 65535. Default: 0. |
| `resource_uri` | string | The URI that identifies this resource. |
| `role` | string | The level of privileges the participant will had in the conference. host: The participant had full privileges. guest: The participant had restricted privileges. |
| `rx_bandwidth` | integer | The maximum inbound bandwidth (in kbps) available for the call. |
| `service_tag` | string | The unique identifier used to track usage of the service. Maximum length: 250 characters. |
| `service_type` | string | The type of service the participant was connected to. |
| `signalling_node` | string | The Conferencing Node the participant was connected to for call signaling. Maximum length: 50 characters. |
| `start_time` | datetime | The time at which the participant connected. |
| `system_location` | string | The system location of the participant. Maximum length: 250 characters. |
| `transcoding_enabled` | boolean | Indicates whether transcoding was enabled for this participant's media. |
| `tx_bandwidth` | integer | The maximum outbound bandwidth (in kbps) available for the call. |
| `vendor` | string | The vendor information for the endpoint. Maximum length: 200 characters. |
