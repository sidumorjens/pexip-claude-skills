# /api/admin/configuration/v1/upgrade/

**Endpoint:** `/api/admin/configuration/v1/upgrade/`

## Allowed methods

- **Allowed Methods (list):** POST

## Fields

| Field | Type | Description |
|---|---|---|
| `package` | string | The package containing the new software. |
| `request` | boolean | Create an upgrade request |
| `total_size` | integer | Total size of upgrade package when creating an upgrade request. |
