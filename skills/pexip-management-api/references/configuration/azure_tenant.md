# Teams Tenant

**Endpoint:** `/api/admin/configuration/v1/azure_tenant/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `description` | string | The description of the Teams tenant. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `name` | string | The name used to refer to this Teams tenant. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `tenant_id` | string | The Azure tenant ID where the Microsoft Teams users are homed. |
