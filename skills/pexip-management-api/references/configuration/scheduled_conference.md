# Scheduled Conference

**Endpoint:** `/api/admin/configuration/v1/scheduled_conference/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `conference` | `conference` (related resource) | A single related resource. Can be either a URI or set of nested resource data. |
| `end_time` | datetime | The time at which the scheduled conference is due to end. |
| `ews_item_id` | string | The ID of the Exchange Web Services Item this scheduled conference is associated with. Maximum length: 255 characters. |
| `ews_item_uid` | string | The UID of the Exchange Web Services Item this scheduled conference is associated with. Maximum length: 255 characters. |
| `id` | integer | The primary key. |
| `recurring_conference` | `recurring_conference` (related resource) | The related recurring conference if this scheduled conference is an occurrence in a recurring series. |
| `resource_uri` | string | The URI that identifies this resource. |
| `scheduled_alias` | `scheduled_alias` (related resource) | The scheduled alias that this scheduled conference has been assigned. |
| `start_time` | datetime | The time at which the scheduled conference is due to start. |
| `subject` | string | The subject that was used in the meeting email. Maximum length: 255 characters. |
