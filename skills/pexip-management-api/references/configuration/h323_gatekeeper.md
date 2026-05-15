# H.323 gatekeeper

**Endpoint:** `/api/admin/configuration/v1/h323_gatekeeper/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `address` | string | The IPv4 address or hostname of the H.323 gatekeeper. Maximum length: 255 characters. |
| `description` | string | A description of the H.323 gatekeeper. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `name` | string | The name used to refer to this H.323 gatekeeper. Maximum length: 250 characters. |
| `port` | integer | The RAS port of the H.323 gatekeeper. Range: 1 to 65535. Default: 1719. |
| `resource_uri` | string | The URI that identifies this resource. |
