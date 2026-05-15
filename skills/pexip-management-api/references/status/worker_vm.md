# Conferencing Node

**Endpoint:** `/api/admin/status/v1/worker_vm/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `boot_time` | datetime | The time at which the Virtual Machine was last booted. |
| `configuration_id` | integer | The primary key of the Conferencing Node configuration. |
| `cpu_capabilities` | string | The highest CPU instruction set supported by this Virtual Machine. |
| `cpu_count` | integer | The configured number of virtual CPUs on this system. |
| `cpu_model` | string | The underlying CPU model for this Virtual Machine. |
| `deploy_status` | string | This reflects whether the Conferencing Node has reported to the management node or not. |
| `hypervisor` | string | The hypervisor on which this Virtual Machine is running. |
| `id` | integer | The primary key. |
| `last_attempted_contact` | datetime | The last time at which an attempt to contact the Conferencing Node was made. |
| `last_updated` | datetime | The time at which the Conferencing Node was last updated. |
| `maintenance_mode` | boolean | Indicates whether the Conferencing Node is in maintenance mode. |
| `maintenance_mode_reason` | string | A description for the reason we are in maintenance mode. Maximum length: 250 characters. |
| `max_audio_calls` | integer | An estimate of the maximum audio call capacity for the Conferencing Node. |
| `max_direct_participants` | integer | The maximum direct media participant capacity for the Conferencing Node. |
| `max_full_hd_calls` | integer | An estimate of the maximum full high definition call capacity for the Conferencing Node. |
| `max_hd_calls` | integer | An estimate of the maximum high definition call capacity for the Conferencing Node. |
| `max_media_tokens` | integer | An estimate of the maximum media token capacity for the Conferencing Node. |
| `max_sd_calls` | integer | An estimate of the maximum standard definition call capacity for the Conferencing Node. |
| `media_load` | integer | Media load |
| `media_tokens_used` | integer | The number of media tokens allocated to calls in progress on the Conferencing Node. |
| `name` | string | The name used to refer to this Conferencing Node. Maximum length: 32 characters. |
| `node_type` | string | The type of this node. |
| `resource_uri` | string | The URI that identifies this resource. |
| `signaling_count` | integer | Count of calls using this Conferencing Node for signalling. |
| `sync_status` | string | This node's configuration synchronisation state. |
| `system_location` | string | The system location for this Conferencing Node. Maximum length: 250 characters. |
| `total_ram` | integer | The amount of RAM (in KB) configured on this Virtual Machine. |
| `upgrade_status` | string | The current upgrade status of the Conferencing Node. |
| `version` | string | The currently installed software version on the Conferencing Node. |
