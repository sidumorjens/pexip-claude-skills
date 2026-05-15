# LDAP sync source

**Endpoint:** `/api/admin/configuration/v1/ldap_sync_source/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `description` | string | A description of the LDAP synchronization source. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `ldap_base_dn` | string | The base DN of the LDAP forest to query (e.g. dc=example,dc=com). Maximum length: 255 characters. |
| `ldap_bind_password` | string | The password used to bind to the LDAP server. Maximum length: 100 characters. |
| `ldap_bind_username` | string | The username used to bind to the LDAP server. This should be a domain user service account, not the Administrator account. Maximum length: 255 characters. |
| `ldap_permit_no_tls` | boolean | Permit LDAP queries to be sent over an insecure connection. |
| `ldap_server` | string | The hostname of the LDAP server. Enter a domain name for DNS SRV lookup or an FQDN for DNS A/AAAA lookup, and ensure that it is resolvable over DNS. Maximum length: 255 characters. |
| `ldap_use_global_catalog` | boolean | Search the Active Directory Global Catalog instead of traditional LDAP. |
| `name` | string | The name of this LDAP synchronization source. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
