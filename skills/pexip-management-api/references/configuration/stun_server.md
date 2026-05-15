# STUN server

**Endpoint:** `/api/admin/configuration/v1/stun_server/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `address` | string | The IP address or FQDN of the STUN server. Maximum length: 255 characters. |
| `description` | string | A description of the STUN server. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `name` | string | The name used to refer to this STUN server. Maximum length: 250 characters. |
| `port` | integer | The IP port on the STUN server to which the Conferencing Node will connect. Range: 1 to 65535. Default: 3478. |
| `resource_uri` | string | The URI that identifies this resource. |
