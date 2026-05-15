# Exchange Scheduler

**Endpoint:** `/api/admin/status/v1/exchange_scheduler/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `exchange_connector_id` | integer | The primary key of the Secure Scheduler for Exchange Integration associated with this status. |
| `id` | integer | The primary key. |
| `last_modified_time` | datetime | Indicates the time the scheduler last successfully processed an item. |
| `resource_uri` | string | The URI that identifies this resource. |
