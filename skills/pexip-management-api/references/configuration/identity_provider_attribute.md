# Identity Provider Attribute

**Endpoint:** `/api/admin/configuration/v1/identity_provider_attribute/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `description` | string | A description of the Identity Provider Attribute. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `name` | string | The name of the attribute in the Identity Provider's response. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
