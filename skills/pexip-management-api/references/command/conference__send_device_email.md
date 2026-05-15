# /api/admin/command/v1/conference/send_device_email/

**Endpoint:** `/api/admin/command/v1/conference/send_device_email/`

## Allowed methods

- **Allowed Methods (list):** POST

## Fields

| Field | Type | Description |
|---|---|---|
| `conference_sync_template_id` | integer | Optional: id of the conference_sync_template email settings to use instead of the default |
| `device_id` | integer | The unique identifier of the device to send a reminder email for. |
