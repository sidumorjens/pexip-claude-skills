# Cloud Node

**Endpoint:** `/api/admin/status/v1/cloud_node/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `aws_instance_id` | string | Deprecated field - use cloud_instance_id field instead. |
| `aws_instance_ip` | string | Deprecated field - use cloud_instance_ip field instead. |
| `aws_instance_launch_time` | datetime | Deprecated field - use cloud_instance_launch_time field instead. |
| `aws_instance_name` | string | Deprecated field - use cloud_instance_name field instead. |
| `aws_instance_state` | string | Deprecated field - use cloud_instance_state field instead. |
| `cloud_instance_id` | string | Cloud instance ID |
| `cloud_instance_ip` | string | Node IP |
| `cloud_instance_launch_time` | datetime | Start time |
| `cloud_instance_name` | string | Cloud instance name |
| `cloud_instance_state` | string | State |
| `max_hd_calls` | integer | Max HD connections |
| `media_load` | integer | Media load |
| `resource_uri` | string | The URI that identifies this resource. |
| `workervm_configuration_id` | integer | The primary key of the Conferencing Node configuration. |
| `workervm_configuration_location_name` | string | The system location for this Conferencing Node. |
| `workervm_configuration_name` | string | The name of the Conferencing Node. |
