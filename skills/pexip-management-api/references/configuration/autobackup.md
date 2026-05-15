# Automatic backups

**Endpoint:** `/api/admin/configuration/v1/autobackup/`

## Allowed methods

- **Allowed Methods (list):** GET
- **Allowed Methods (detail):** GET, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `autobackup_enabled` | boolean | Enable automatic creation of daily configuration backups. Each backup is taken at 01:02 UTC every day. |
| `autobackup_interval` | integer | The number of hours between running an automatic backup. Range: 1 to 24. Default: 24. |
| `autobackup_passphrase` | string | The passphrase used to encrypt all automatically generated backup files. Maximum length: 100 characters. |
| `autobackup_start_hour` | integer | The hour (in UTC time) to run the automatic backup. This can run multiple times a day by adjusting the interval. Range: 0 to 23. Default: 1. |
| `autobackup_upload_password` | string | The password for the upload URL. Maximum length: 100 characters. |
| `autobackup_upload_url` | string | The URL to which to upload automatic backups. Supported schemes: FTPS, FTP. Maximum length: 255 characters. |
| `autobackup_upload_username` | string | The username for the upload URL. Maximum length: 100 characters. |
| `id` | integer | The primary key. |
| `resource_uri` | string | The URI that identifies this resource. |
