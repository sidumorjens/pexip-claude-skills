# Log level

**Endpoint:** `/api/admin/configuration/v1/log_level/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `id` | integer | The primary key. |
| `level` | string | The level of logging for this logger. |
| `name` | string | The name of the logger. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
