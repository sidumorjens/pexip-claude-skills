# Role Mapping

**Endpoint:** `/api/admin/configuration/v1/role_mapping/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `id` | integer | The primary key. |
| `name` | string | A descriptive name for this role mapping. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `roles` | `role` (related resource) | The role(s) to assign matching users to. |
| `source` | string | The authentication source to which this role mapping applies. |
| `value` | string | The group within the OIDC provider to which this role mapping applies. For Azure this will be the Object ID; for Okta it will be the group name. This group must be included in the list that is returned in the specified Groups field of the authentication token response. If the Groups field is blank, this value will be ignored.  Maximum length: 255 characters. |
