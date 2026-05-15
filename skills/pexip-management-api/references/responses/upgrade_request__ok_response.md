# /response/upgrade_request/ok_response/

**Endpoint:** `/response/upgrade_request/ok_response/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `current` | `version_info` (related resource) | Current software version running on the system. |
| `next_url` | string | Returned by the /finish/ endpoint, this is the Management Admin UI URL to navigate to to confirm (if validate_only was true) or monitor the upgrade. |
| `ok` | boolean | Always true. HTTP 400 Bad Request returned if this would be false. |
| `timestamp` | integer | Server timestamp to measure how long a chunk upload has taken. |
| `upgrade` | `version_info` (related resource) | Upgrade software version contained in the uploaded package. |
| `upload_id` | string | Upgrade upload request ID. |
