# User Group Mapping

**Endpoint:** `/api/admin/configuration/v1/user_group_entity_mapping/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `description` | string | The description of this entiity mapping. Maximum length: 250 characters. |
| `entity_resource_uri` | string | Resource URI for the corresponding resource. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `resource_uri` | string | The URI that identifies this resource. |
| `user_group` | `user_group` (related resource) | The Group Name of this user group. |
