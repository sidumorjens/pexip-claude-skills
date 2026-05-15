# SIP proxy

**Endpoint:** `/api/admin/configuration/v1/sip_proxy/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `address` | string | The IP address or FQDN of the SIP proxy. Maximum length: 255 characters. |
| `description` | string | A description of the SIP proxy. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `name` | string | The name used to refer to this SIP proxy. Maximum length: 250 characters. |
| `port` | integer | The IP port of the SIP proxy. Range: 1 to 65535. Default: 5061. |
| `resource_uri` | string | The URI that identifies this resource. |
| `transport` | string | The IP transport used to connect to the SIP proxy. |
