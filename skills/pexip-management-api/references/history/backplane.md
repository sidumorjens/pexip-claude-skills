# Backplane

**Endpoint:** `/api/admin/history/v1/backplane/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `conference` | `conference` (related resource) | A single related resource. Can be either a URI or set of nested resource data. |
| `conference_name` | string | The name used to refer to the service. Maximum length: 250 characters. |
| `disconnect_reason` | string | The reason the backplane was disconnected. Maximum length: 250 characters. |
| `duration` | integer | The duration of the call in seconds. |
| `end_time` | datetime | The time at which the backplane disconnected. |
| `id` | string | The primary key. |
| `media_node` | string | The local Conferencing Node the backplane was connected to. Maximum length: 50 characters. |
| `media_streams` | `media_stream` (related resource) | The media streams created by the backplane. |
| `protocol` | string | The signaling protocol for the backplane call. |
| `proxy_node` | string | The Proxying Edge Node that was proxying media for the backplane. Maximum length: 50 characters. |
| `remote_conference_name` | string | The remote conference the backplane was connected to. Maximum length: 250 characters. |
| `remote_media_node` | string | The remote Conferencing Node the backplane was connected to. Maximum length: 50 characters. |
| `remote_node_name` | string | The remote name the backplane was connected to. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `service_tag` | string | The unique identifier used to track usage of the service. Maximum length: 250 characters. |
| `start_time` | datetime | The time at which the backplane connected. |
| `system_location` | string | The system location of the backplane. Maximum length: 250 characters. |
| `type` | string | The type of backplane between Conferencing Nodes. |
