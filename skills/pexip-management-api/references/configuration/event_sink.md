# Event sink

**Endpoint:** `/api/admin/configuration/v1/event_sink/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `bulk_support` | boolean | When enabled, all events received during a set interval are batched together and sent in a single message. |
| `description` | string | A description of the event sink. Maximum length: 250 characters. |
| `events` | `event_sink_event` (related resource) | The list of events to send to this event sink. |
| `filter_events` | boolean | When enabled, it is possible to select which named events to send to the event sink. |
| `id` | integer | The primary key. |
| `name` | string | The name used to refer to this event sink. Each event sink must have a unique name. Maximum length: 250 characters. |
| `password` | string | The password used to authenticate to the external server when sending events. The password is case-sensitive. Maximum length: 100 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `restart_date` | datetime | The time and date that a request to restart the eventsink publisher was requested. |
| `updated_at` | datetime | The time and date of the last configuration change to this eventsink. |
| `url` | string | The URL of the external server to which events are sent. Maximum length: 255 characters. |
| `username` | string | The username used to authenticate to the external server when sending events. The username is case-sensitive. Leave empty if no authentication is required. Maximum length: 100 characters. |
| `verify_tls_certificate` | boolean | Whether to enable TLS verification when sending events. Only valid if the URL is HTTPS. |
| `version` | integer | The internal Pexip protocol version supported by this event sink. |
