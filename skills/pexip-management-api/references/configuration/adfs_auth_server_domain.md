# AD FS Domain

**Endpoint:** `/api/admin/configuration/v1/adfs_auth_server_domain/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `adfs_auth_server` | `adfs_auth_server` (related resource) | A single related resource. Can be either a URI or set of nested resource data. |
| `description` | string | A description of the domain. Maximum length: 250 characters. |
| `domain` | string | The FQDN which, when present in a user's email address, will permit that user to authenticate using AD FS. For example, if a user has the email bob@example.com, example.com must be entered as a domain to allow that user to sign on with AD FS. Maximum length: 192 characters. |
| `id` | integer | The primary key. |
| `resource_uri` | string | The URI that identifies this resource. |
