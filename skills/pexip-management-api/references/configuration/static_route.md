# Static route

**Endpoint:** `/api/admin/configuration/v1/static_route/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `address` | string | The IP address to be used in conjunction with the Network prefix to determine the network addresses to which this route applies. |
| `gateway` | string | The IP address of the gateway to the network for this route. |
| `id` | integer | The primary key. |
| `name` | string | The name of the static route. Maximum length: 32 characters. |
| `prefix` | integer | The prefix length used in conjunction with the Destination network address to determine the network addresses to which this route applies. For example, use a Destination network address of 10.0.0.0 and a Network prefix of 8 to route addresses in the range 10.0.0.0 to 10.255.255.255. Range: 0 to 128. |
| `resource_uri` | string | The URI that identifies this resource. |
