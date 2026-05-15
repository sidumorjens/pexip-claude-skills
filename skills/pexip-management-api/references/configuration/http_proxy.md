# Web proxy

**Endpoint:** `/api/admin/configuration/v1/http_proxy/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `address` | string | The IP address or FQDN of the proxy server. Maximum length: 255 characters. |
| `id` | integer | The primary key. |
| `name` | string | The name used to refer to this proxy server. Maximum length: 250 characters. |
| `password` | string | The password used when accessing the proxy server. Maximum length: 100 characters. |
| `port` | integer | The IP port of the proxy server. Range: 1 to 65535. Default: 8080. |
| `protocol` | string | The protocol used to connect to the proxy server. |
| `resource_uri` | string | The URI that identifies this resource. |
| `username` | string | The username used when accessing the proxy server. Maximum length: 100 characters. |
