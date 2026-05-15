# System location

**Endpoint:** `/api/admin/status/v1/system_location/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `id` | integer | The primary key. |
| `max_audio_calls` | integer | Maximum capacity - audio connections |
| `max_connections` | string | Maximum connections by node type (comma separated list of node type and maximum number of connections) |
| `max_full_hd_calls` | integer | Maximum capacity - Full HD connections |
| `max_hd_calls` | integer | Maximum capacity - HD connections |
| `max_media_tokens` | integer | Maximum capacity - media tokens |
| `max_sd_calls` | integer | Maximum capacity - SD connections |
| `media_load` | float | A percentage estimate of the current media load average across the Conferencing Nodes in the system location |
| `media_tokens_used` | integer | Used capacity - media tokens |
| `name` | string | The name used to refer to this system location. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
