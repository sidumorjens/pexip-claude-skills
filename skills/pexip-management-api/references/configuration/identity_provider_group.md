# Identity Provider Group

**Endpoint:** `/api/admin/configuration/v1/identity_provider_group/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `description` | string | A description of the Identity Provider Group. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `identity_provider` | `identity_provider` (related resource) | The Identity Providers that will be accepted when this Identity Provider Group is in use. |
| `name` | string | The name used to refer to this Identity Provider Group. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
