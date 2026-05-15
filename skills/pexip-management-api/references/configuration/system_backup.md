# Backup

**Endpoint:** `/api/admin/configuration/v1/system_backup/`

## Allowed methods

- **Allowed Methods (list):** GET
- **Allowed Methods (detail):** GET, DELETE

## Fields

| Field | Type | Description |
|---|---|---|
| `build` | string | The software build for the system the backup was taken. |
| `date` | datetime | The date the system backup was taken. |
| `filename` | string | The filename of the system backup. |
| `resource_uri` | string | The URI that identifies this resource. |
| `sha256sum` | string | SHA-256 checksum of the backup file |
| `size` | integer | The size of the backup file. |
| `type` | string | The type of system backup. |
| `version` | string | The software version of the system for which the backup was taken. |
