# User Group

**Endpoint:** `/api/admin/configuration/v1/user_group/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `description` | string | The description of the user group. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `name` | string | The name used to refer to this User Group. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `user_group_entity_mappings` | `user_group_entity_mapping` (related resource) | The resource mappings that this user group has. |
| `users` | `end_user` (related resource) | The user which belongs to this group |
