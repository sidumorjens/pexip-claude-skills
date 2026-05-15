# Participant

**Endpoint:** `/api/admin/status/v1/participant/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `bandwidth` | integer | The maximum bandwidth (in kbps) available for the call. |
| `call_direction` | string | The direction of the call. |
| `call_quality` | string | The overall quality of the call based on packet loss. |
| `call_tag` | string | Optional client-supplied identifier for this call. Maximum length: 1000 characters. |
| `call_uuid` | string | The unique identifier of the participant call. Maximum length: 200 characters. |
| `conference` | string | The name of the service for this conference. Maximum length: 250 characters. |
| `connect_time` | datetime | The time at which the participant connected. |
| `conversation_id` | string | A unique identifier to correlate multiple related calls. |
| `destination_alias` | string | The destination alias of the call. Maximum length: 1000 characters. |
| `display_name` | string | The display name of the participant. Maximum length: 1000 characters. |
| `encryption` | string | The media encryption status for the call. |
| `has_media` | boolean | Whether the participant is transmitting or receiving media streams. |
| `id` | string | The primary key. |
| `idp_uuid` | string | Indicates the Identity Provider that authenticated the participant. |
| `is_client_muted` | boolean | Indicates whether the participant has muted itself. |
| `is_direct` | boolean | Indicates whether the participant is in a direct media conference. |
| `is_disconnect_supported` | boolean | Indicates whether the endpoint can be disconnected. |
| `is_idp_authenticated` | boolean | Indicates whether the participant was authenticated by an Identity Provider. |
| `is_mute_supported` | boolean | Indicates whether the endpoint mute state can be modified. |
| `is_muted` | boolean | Indicates whether the participant has been administratively muted. |
| `is_on_hold` | boolean | Indicates whether the participant has been placed on hold. |
| `is_presentation_supported` | boolean | Indicates whether the endpoint supports presentation streams. |
| `is_presenting` | boolean | Indicates whether the participant is presenting. |
| `is_recording` | boolean | Indicates whether the participant is recording. |
| `is_streaming` | boolean | Indicates whether the participant is a streaming or recording device. |
| `is_transcribing` | boolean | Indicates whether the participant is transcribing. |
| `is_transfer_supported` | boolean | Indicates whether the endpoint can be transferred. |
| `license_count` | integer | The number of licenses consumed by the participant. |
| `license_type` | string | The number of licenses consumed by the participant. |
| `media_node` | string | The Conferencing Node the participant is connected to for call media. Maximum length: 50 characters. |
| `parent_id` | string | This field is deprecated and will be ignored. |
| `participant_alias` | string | The alias of the participant. |
| `protocol` | string | The signaling protocol for the call. |
| `proxy_node` | string | The Proxying Edge Node that is proxying media for the participant. Maximum length: 50 characters. |
| `remote_address` | string | The remote IP address used for signaling. Maximum length: 50 characters. |
| `remote_port` | integer | The IP port used for signaling. Range: 0 to 65535. Default: 0. |
| `resource_uri` | string | The URI that identifies this resource. |
| `role` | string | The level of privileges the participant will have in the conference. host: The participant will have full privileges. guest: The participant will have restricted privileges. |
| `rx_bandwidth` | integer | The maximum inbound bandwidth (in kbps) available for the call. |
| `service_tag` | string | The unique identifier used to track usage of the service. Maximum length: 250 characters. |
| `service_type` | string | The type of service the participant is connected to. |
| `signalling_node` | string | The Conferencing Node the participant is connected to for call signaling. Maximum length: 50 characters. |
| `source_alias` | string | The source alias of the call. Maximum length: 1000 characters. |
| `system_location` | string | The system location of the participant. Maximum length: 250 characters. |
| `transcoding_enabled` | boolean | Indicates whether transcoding is enabled for this participant. |
| `tx_bandwidth` | integer | The maximum outbound bandwidth (in kbps) available for the call. |
| `vendor` | string | The vendor information for the endpoint. Maximum length: 200 characters. |
