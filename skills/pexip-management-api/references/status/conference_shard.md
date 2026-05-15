# Conference shard

**Endpoint:** `/api/admin/status/v1/conference_shard/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `conference` | string | The name of the service for this conference. Maximum length: 250 characters. |
| `guests_muted` | boolean | Whether all Guests are administratively muted. |
| `id` | string | The primary key. |
| `is_direct` | boolean | Whether the conference is currently using direct media |
| `is_locked` | boolean | Indicates whether the conference has been locked. |
| `is_started` | boolean | Whether the conference has been started by a Host being present. |
| `node` | string | The IPv4 address of the Conferencing Node. Maximum length: 50 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `service_type` | string | The type of conferencing service. conference: A Virtual Meeting Room. lecture: A Virtual Auditorium. two_stage_dialing: A Virtual Reception. |
| `start_time` | datetime | The time at which the conference started. |
| `system_location` | string | The system location for this conference. Maximum length: 250 characters. |
| `tag` | string | The unique identifier used to track usage of the service. Maximum length: 250 characters. |
| `transcoding_enabled` | boolean | Whether media transcoding is enabled for this conference |
