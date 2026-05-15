# Conference

**Endpoint:** `/api/admin/status/v1/conference/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `direct_media_available` | boolean | Indicates if this conference was configured to use direct media where possible. Does not confirm if this conference was always direct. |
| `guests_muted` | boolean | Whether all Guests have been muted in the conference. |
| `id` | string | The primary key. |
| `is_locked` | boolean | Indicates whether the conference has been locked. |
| `is_started` | boolean | Whether the conference has started by a Host being present. |
| `name` | string | The name of the service for this conference. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `service_type` | string | The type of conferencing service. conference: A Virtual Meeting Room. lecture: A Virtual Auditorium. two_stage_dialing: A Virtual Reception. |
| `start_time` | datetime | The time at which the conference started. |
| `tag` | string | The unique identifier used to track usage of the service. Maximum length: 250 characters. |
