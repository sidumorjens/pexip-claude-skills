# Teams Connector node

**Endpoint:** `/api/admin/status/v1/teamsnode/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `call_count` | integer | Number of calls being handled by this teams node |
| `eventhub_id` | string | The unique identifier of the queue. |
| `heartbeat_time` | datetime | Latest Teams Connector node heartbeat time. |
| `id` | string | The primary key. |
| `instance_status` | string | Teams Connector Instance Status. |
| `ip_address` | string | Node IP address. |
| `max_calls` | integer | Maximum call capacity. |
| `media_load` | integer | Media load of this teams node |
| `name` | string | Teams Connector node name. |
| `private_ip_address` | string | Node private IP address. |
| `resource_uri` | string | The URI that identifies this resource. |
| `scaleset_id` | string | Teams Connector. |
| `start_time` | datetime | Start-up time. |
| `state` | string | Teams Connector node status. |
