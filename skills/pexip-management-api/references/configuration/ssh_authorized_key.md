# SSH Authorized Key

**Endpoint:** `/api/admin/configuration/v1/ssh_authorized_key/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `comment` | string | SSH authorized key comment. Maximum length: 8192 characters |
| `id` | integer | The primary key. |
| `key` | string | SSH authorized key public data. |
| `keytype` | string | SSH authorized key type. |
| `nodes` | list | The nodes which are configured to use this SSH authorized key. |
| `resource_uri` | string | The URI that identifies this resource. |
