# Alarm

**Endpoint:** `/api/admin/history/v1/alarm/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `details` | string | Details about this alarm. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `identifier` | integer | Identifier |
| `instance` | string | The instance of this alarm. Maximum length: 250 characters. |
| `level` | string | The severity level of this alarm. |
| `name` | string | The name of this alarm. |
| `node` | string | The IPv4 address of the node. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `time_lowered` | datetime | The time at which the alarm was lowered. |
| `time_raised` | datetime | The time at which the alarm was raised. |
