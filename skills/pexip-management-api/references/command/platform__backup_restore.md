# /api/admin/command/v1/platform/backup_restore/

**Endpoint:** `/api/admin/command/v1/platform/backup_restore/`

## Allowed methods

- **Allowed Methods (list):** POST

## Fields

| Field | Type | Description |
|---|---|---|
| `package` | string | The backup file to be restored. |
| `passphrase` | string | The passphrase that was used to create the backup file. Maximum length: 1000 characters. |
