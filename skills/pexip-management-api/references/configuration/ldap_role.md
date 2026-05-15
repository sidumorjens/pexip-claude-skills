# Role Mapping

**Endpoint:** `/api/admin/configuration/v1/ldap_role/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `ldap_group_dn` | string | The DN of the LDAP group to which this role mapping applies. Maximum length: 255 characters. |
| `name` | string | A descriptive name for this role mapping. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `roles` | `role` (related resource) | The role(s) to assign matching users to. |
