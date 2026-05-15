# Administrator role

**Endpoint:** `/api/admin/configuration/v1/role/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `id` | integer | Integer data. Ex: 2673 |
| `name` | string | Unicode string data. Ex: "Hello World" |
| `permissions` | `permission` (related resource) | The permitted actions for accounts with this role. |
| `resource_uri` | string | The URI that identifies this resource. |
