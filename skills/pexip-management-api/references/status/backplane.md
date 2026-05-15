# Backplane

**Endpoint:** `/api/admin/status/v1/backplane/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `conference` | string | The name of the service for this conference. Maximum length: 250 characters. |
| `connect_time` | datetime | The time at which the participant connected. |
| `id` | string | The primary key. |
| `media_node` | string | The Conferencing Node the participant is connected to for call media. Maximum length: 50 characters. |
| `protocol` | string | The protocol used on the backplane. |
| `proxy_node` | string | The Proxying Edge Node that is proxying media for the participant. Maximum length: 50 characters. |
| `remote_conference_name` | string | The remote conference the backplane is connected to. Maximum length: 250 characters. |
| `remote_media_node` | string | The remote Conferencing Node the backplane is connected to for call media. Maximum length: 50 characters. |
| `remote_node_name` | string | The remote name the backplane is connected to. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `service_tag` | string | The unique identifier used to track usage of the service. Maximum length: 250 characters. |
| `system_location` | string | The system location of the participant. Maximum length: 250 characters. |
| `type` | string | The type of backplane between Conferencing Nodes. local: A backplane between Conferencing Nodes within the same system location. geo: A backplane between Conferencing Nodes in different system locations. |
