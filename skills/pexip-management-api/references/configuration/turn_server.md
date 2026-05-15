# TURN server

**Endpoint:** `/api/admin/configuration/v1/turn_server/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `address` | string | The IP address or FQDN of the TURN server. Maximum length: 255 characters. |
| `description` | string | A description of the TURN server. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `name` | string | The name used to refer to this TURN server. Maximum length: 250 characters. |
| `password` | string | The password of a valid account on the TURN server. Maximum length: 100 characters. |
| `port` | integer | The IP port on the TURN server to which the Conferencing Node or Pexip app will connect. Range: 1 to 65535. Default: 3478. |
| `resource_uri` | string | The URI that identifies this resource. |
| `secret_key` | string | Shared secret to be used with TURN server time-limited credentials. Maximum length: 100 characters. |
| `server_type` | string | Type of TURN server and TURN server authentication. |
| `transport_type` | string | Network transport type for communication with the TURN server. |
| `username` | string | The username of a valid account on the TURN server. Maximum length: 100 characters. |
