# Backup request

**Endpoint:** `/api/admin/status/v1/backup_request/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `created_at` | datetime | The date and time when the snapshot was requested. |
| `download_uri` | string | The URI to download the requested file. |
| `message` | string | An error message from the snapshot generation process. |
| `resource_uri` | string | The URI that identifies this resource. |
| `state` | string | Status of snapshot request. |
| `updated_at` | datetime | The date and time this snapshot request was last updated. |
