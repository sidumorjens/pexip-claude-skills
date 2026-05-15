# Skype for Business server

**Endpoint:** `/api/admin/configuration/v1/mssip_proxy/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `address` | string | The IP address or FQDN of the Skype for Business server to use for outbound MS-SIP calls. This can be a Front End Server or Director; it cannot be an Edge Server. Maximum length: 255 characters. |
| `description` | string | A description of the Skype for Business server. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `name` | string | The name used to refer to this Skype for Business server. Maximum length: 250 characters. |
| `port` | integer | The IP port of the Skype for Business server. Range: 1 to 65535. Default: 5061. |
| `resource_uri` | string | The URI that identifies this resource. |
| `transport` | string | The IP transport used to connect to the Skype for Business server. |
