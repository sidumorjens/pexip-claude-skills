# Scheduled Alias

**Endpoint:** `/api/admin/configuration/v1/scheduled_alias/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `alias` | string | The alias which has been generated for a scheduled conference. Maximum length: 250 characters. |
| `alias_number` | integer | The alias number which has been generated for a scheduled conference. Minimum value: 0. |
| `conference_deletion_time` | datetime | The time at which the conference using this scheduled alias was deleted. |
| `creation_time` | datetime | The time at which the scheduled alias was created. |
| `ews_item_uid` | string | The UID of the Exchange Web Services Item this scheduled alias is associated with. Maximum length: 255 characters. |
| `exchange_connector` | `ms_exchange_connector` (related resource) | The Secure Scheduler for Exchange Integration that is responsible for this scheduled alias. |
| `id` | integer | The primary key. |
| `is_used` | boolean | Indicates whether or not this scheduled alias has been used by a conference. |
| `numeric_alias` | string | The numeric alias which has been generated for a scheduled conference. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `uuid` | string | Unique identifier for the alias. |
