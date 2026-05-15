# Conferencing Node event

**Endpoint:** `/api/admin/history/v1/workervm_status_event/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `context` | string | The context of the Conferencing Node status event. Maximum length: 250 characters. |
| `details` | string | Details about this Conferencing Node status event. Maximum length: 250 characters. |
| `event_type` | string | The type of event which occurred on this Conferencing Node |
| `id` | integer | The primary key. |
| `resource_uri` | string | The URI that identifies this resource. |
| `state` | string | The new state that the Conferencing Node is now in. |
| `time_changed` | datetime | The time at which the cloud node status was changed. |
| `workervm_address` | string | Node IP |
| `workervm_configuration_id` | integer | The primary key of the Conferencing Node configuration. |
| `workervm_configuration_location_name` | string | The system location for this Conferencing Node. |
| `workervm_configuration_name` | string | Conferencing Node |
