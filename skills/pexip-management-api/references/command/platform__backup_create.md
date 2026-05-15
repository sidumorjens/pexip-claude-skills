# /api/admin/command/v1/platform/backup_create/

**Endpoint:** `/api/admin/command/v1/platform/backup_create/`

## Allowed methods

- **Allowed Methods (list):** POST

## Fields

| Field | Type | Description |
|---|---|---|
| `passphrase` | string | The passphrase to be used to encrypt the new backup file. Maximum length: 1000 characters. |
| `request` | boolean | Set to true to create a background backup creation request instead |
