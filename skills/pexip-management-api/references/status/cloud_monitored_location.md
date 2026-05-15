# Monitored location

**Endpoint:** `/api/admin/status/v1/cloud_monitored_location/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `free_hd_calls` | integer | Available HD connections |
| `id` | integer | The primary key. |
| `max_hd_calls` | integer | Max HD connections |
| `media_load` | integer | Media load |
| `name` | string | The name of this monitored location. |
| `overflow_location` | `cloud_overflow_location` (related resource) | Overflow location |
| `resource_uri` | string | The URI that identifies this resource. |
