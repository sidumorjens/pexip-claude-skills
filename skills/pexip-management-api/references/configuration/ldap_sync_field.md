# LDAP sync field

**Endpoint:** `/api/admin/configuration/v1/ldap_sync_field/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `description` | string | A description of the LDAP sync field. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `is_binary` | boolean | Select this to enable special  handling of this LDAP field; needed for special fields such as GUIDs (should not be used for ordinary textual or numeric LDAP fields). |
| `name` | string | The name of the LDAP attribute (case sensitive) to be read from the LDAP server (may contain hyphens). Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `template_variable_name` | string | The name of the variable to use in LDAP sync templates that will contain the value of the LDAP field. We recommend that you set this name to something similar to the LDAP field name, but note that this name cannot contain hyphens. Maximum length: 250 characters. |
