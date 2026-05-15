# Scheduling operation

**Endpoint:** `/api/admin/status/v1/scheduling_operation/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `creation_time` | datetime | The time at which the scheduling operation was created. |
| `error_code` | string | The error code if the scheduling operation failed. Maximum length: 50 characters. |
| `error_description` | string | The error description of why the scheduling operation failed. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `resource_id` | integer | The ID of the resource which was created by this scheduling operation, if any. |
| `resource_uri` | string | The URI that identifies this resource. |
| `success` | boolean | Indicates whether or not this scheduling operation completed successfully. |
| `transaction_uuid` | string | Unique identifier for the scheduling operation. |
