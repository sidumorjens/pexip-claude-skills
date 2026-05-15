# Conference

**Endpoint:** `/api/admin/history/v1/conference/`

## Allowed methods

- **Allowed Methods (list):** GET
- **Allowed Methods (detail):** GET, DELETE

## Fields

| Field | Type | Description |
|---|---|---|
| `direct_media_available` | boolean | Indicates if this conference was configured to use direct media where possible. Does not confirm if this conference was always direct. |
| `duration` | integer | The duration of the conference. |
| `end_time` | datetime | The time at which the conference ended. |
| `id` | string | The primary key. |
| `instant_message_count` | integer | The number of instant messages sent in the conference. |
| `name` | string | The name used to refer to the service. Maximum length: 250 characters. |
| `participant_count` | integer | The number of participants that joined the conference. |
| `participants` | `participant` (related resource) | The participants that joined the conference. |
| `resource_uri` | string | The URI that identifies this resource. |
| `service_type` | string | The type of conferencing service. |
| `start_time` | datetime | The time at which the conference started. |
| `tag` | string | The unique identifier used to track usage of the service. Maximum length: 250 characters. |
