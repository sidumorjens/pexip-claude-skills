# Trusted Join Settings

**Endpoint:** `/api/admin/configuration/v1/trusted_join/`

## Allowed methods

- **Allowed Methods (list):** GET
- **Allowed Methods (detail):** GET, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `id` | integer | The primary key. |
| `resource_uri` | string | The URI that identifies this resource. |
| `zoom_enabled` | boolean | This setting enables enhanced interoperability on Zoom calls. |
