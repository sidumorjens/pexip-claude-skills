# Recurring Conference

**Endpoint:** `/api/admin/configuration/v1/recurring_conference/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `conference` | `conference` (related resource) | A single related resource. Can be either a URI or set of nested resource data. |
| `current_index` | integer | The current index of the occurrence in this series that has been scheduled. Minimum value: 0. |
| `ews_item_id` | string | The ID of the Exchange Web Services Item this recurring conference is associated with. Maximum length: 255 characters. |
| `id` | integer | The primary key. |
| `is_depleted` | boolean | Whether or not all occurrences in this series have been depleted. |
| `resource_uri` | string | The URI that identifies this resource. |
| `scheduled_alias` | `scheduled_alias` (related resource) | The scheduled alias that this recurring conference has been assigned. |
| `subject` | string | The subject that was used in the meeting email. Maximum length: 255 characters. |
