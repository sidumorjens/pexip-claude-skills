# DNS server

**Endpoint:** `/api/admin/configuration/v1/dns_server/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `address` | string | The IP address of the DNS server. |
| `description` | string | A description of the DNS server. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `resource_uri` | string | The URI that identifies this resource. |
