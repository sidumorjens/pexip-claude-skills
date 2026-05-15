# teams node call

**Endpoint:** `/api/admin/status/v1/teamsnode_call/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `destination` | string | Teams call destination. |
| `heartbeat_time` | datetime | Latest Teams Connector node call heartbeat time. |
| `id` | string | The primary key. |
| `resource_uri` | string | The URI that identifies this resource. |
| `source` | string | Teams call source. |
| `start_time` | datetime | Teams call start time. |
| `state` | string | Teams Connector node call status. |
| `teamsnode_id` | string | Teams node unique identifier. |
