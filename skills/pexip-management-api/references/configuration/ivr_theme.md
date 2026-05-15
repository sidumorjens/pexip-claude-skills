# Theme

**Endpoint:** `/api/admin/configuration/v1/ivr_theme/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `conference` | `conference` (related resource) | The list of services that will use this theme. |
| `custom_layouts` | string | The Custom layouts available in this theme. (comma separated) |
| `gateway_routing_rule` | `gateway_routing_rule` (related resource) | The list of call routing rules that will use this theme. |
| `id` | integer | The primary key. |
| `last_updated` | datetime | Update Time |
| `name` | string | The name used to refer to this theme. Maximum length: 250 characters. |
| `package` | file | The ZIP file containing the audio and image files that make up the service theme. |
| `pinning_configs` | string | The pinning configurations available in this theme. (comma separated) |
| `resource_uri` | string | The URI that identifies this resource. |
| `uuid` | string | Unique identifier for the theme. |
