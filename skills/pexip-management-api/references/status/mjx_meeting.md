# One-Touch Join Meeting

**Endpoint:** `/api/admin/status/v1/mjx_meeting/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `alias` | string | The meeting alias of this One-Touch Join Meeting. Maximum length: 1000 characters. |
| `end_time` | datetime | The end time of this One-Touch Join Meeting. |
| `endpoint_name` | string | The endpoint name used for this One-Touch Join meeting. |
| `id` | integer | The primary key. |
| `last_modified_time` | datetime | The last modified time of this One-Touch Join Meeting. |
| `matched_meeting_processing_rule` | string | The name of the Meeting Processing Rule that matched this meeting. Maximum length: 50 characters. |
| `meeting_id` | string | The ID of this One-Touch Join Meeting. Maximum length: 200 characters. |
| `mjx_integration_id` | integer | The ID of the One-Touch Join Profile associated with this OTJ Meeting. |
| `mjx_integration_name` | string | The name of the One-Touch Join Profile associated with this OTJ Meeting. Maximum length: 250 characters. |
| `organizer_email` | string | The email address of the organizer of this One-Touch Join Meeting. Maximum length: 100 characters. |
| `organizer_name` | string | The name of the organizer of this One-Touch Join Meeting. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `room_email` | string | The email of the meeting room used for this One-Touch Join Meeting. Maximum length: 150 characters. |
| `start_time` | datetime | The start time of this One-Touch Join Meeting. |
| `subject` | string | The subject of this One-Touch Join Meeting. Maximum length: 1000 characters. |
| `worker_id` | integer | The ID of the Conferencing Node from which this OTJ Meeting was sent. |
