# Administrator authentication

**Endpoint:** `/api/admin/configuration/v1/authentication/`

## Allowed methods

- **Allowed Methods (list):** GET
- **Allowed Methods (detail):** GET, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `api_oauth2_allow_all_perms` | boolean | Allow management API clients authenticated using Oauth2 to use all permissions specified in the assigned role. When this option is disabled, modification of authentication configuration is not allowed even if specific in the role. |
| `api_oauth2_disable_basic` | boolean | Disable basic authentication for management API clients. When this option is selected, access to the management API can only use OAuth. |
| `api_oauth2_expiration` | integer | Specify the access token expiration time in seconds. |
| `client_certificate` | string | Whether to require a client TLS certificate for administrator authentication. Requires LDAP to be included as an authentication source. |
| `id` | integer | The primary key. |
| `ldap_base_dn` | string | The base DN of the LDAP forest to query (e.g. dc=example,dc=com). Maximum length: 255 characters. |
| `ldap_bind_password` | string | The password used to bind to the LDAP server. Maximum length: 100 characters. |
| `ldap_bind_username` | string | The username used to bind to the LDAP server. This should be a domain user service account, not the Administrator account. Maximum length: 255 characters. |
| `ldap_group_filter` | string | The LDAP filter used to match group records in the directory. Default: (\|(objectclass=group)(objectclass=groupOfNames)(objectclass=groupOfUniqueNames)(objectclass=posixGroup)). Maximum length: 1024 characters. |
| `ldap_group_membership_filter` | string | The LDAP filter used to search for group membership of a user. The filter may contain {userdn} to indicate locations into which the user DN is substituted. The filter may contain {useruid} to indicate locations into which the user UID is substituted. This filter will be applied in conjunction with the LDAP group filter and must contain at least one substitution. Default: (\|(member={userdn})(uniquemember={userdn})(memberuid={useruid})). Maximum length: 1024 characters. |
| `ldap_group_search_dn` | string | The DN relative to the base DN to query for group records (e.g. ou=groups). If blank, the base DN will be used. Maximum length: 255 characters. |
| `ldap_permit_no_tls` | boolean | Permit LDAP queries to be sent over an insecure connection. |
| `ldap_server` | string | The hostname of the LDAP server. Enter a domain name for DNS SRV lookup or an FQDN for DNS A/AAAA lookup, and ensure that it is resolvable over DNS. Maximum length: 255 characters. |
| `ldap_use_global_catalog` | boolean | Search the Active Directory Global Catalog instead of traditional LDAP. |
| `ldap_user_filter` | string | The LDAP filter used to match user records in the directory. Default: (&(objectclass=person)(!(objectclass=computer))). Maximum length: 1024 characters. |
| `ldap_user_group_attributes` | string | A comma-separated list of attributes in the LDAP user record to examine for group membership information. The attribute value must contain the DN of each group the user is a member of. If no attributes are specified, or none of the specified attributes are present in the LDAP user record, an LDAP group search will be performed, instead. Default: memberOf. Maximum length: 100 characters. |
| `ldap_user_search_dn` | string | The DN relative to the base DN to query for user records (e.g. ou=people). If blank, the base DN will be used. Maximum length: 255 characters. |
| `ldap_user_search_filter` | string | The LDAP filter used to find user records when given the user name. The filter may contain {username} to indicate locations into which the username is substituted. This filter will be applied in conjunction with the LDAP user filter and must contain at least one substitution. Default: (\|(uid={username})(sAMAccountName={username})). Maximum length: 1024 characters. |
| `oidc_auth_method` | string | The OpenID Connect authentication method. |
| `oidc_authorize_url` | string | The OpenID Connect authorization URL.  This will be loaded from the Metadata URL if provided. |
| `oidc_client_id` | string | The OpenID Connect client ID. |
| `oidc_client_secret` | string | The OpenID Connect client secret to use when authentication method is 'client secret'. |
| `oidc_domain_hint` | string | A domain to pass to the OpenID Connect service as a hint to the expected login account. Maximum length: 255 characters. |
| `oidc_groups_field` | string | The field in the authentication token response to use as the list of groups. You apply role mappings to one or more of these groups by referencing the group in the Role Mapping Value field. If this field is left blank, all users authenticated using OIDC will have the combined access rights of all role mappings that specify a source of OpenID Connect. |
| `oidc_login_button` | string | The text to use for the OpenID Connect button on the login page of the Pexip Infinity Administrator interface. Defaults to OpenID Connect. Maximum length: 128 characters. |
| `oidc_metadata` | string | The OpenID Connect configuration metadata.  This will be loaded from the Metadata URL if provided. |
| `oidc_metadata_url` | string | The URL of the OpenID Connect metadata document, copied from your OIDC provider. |
| `oidc_private_key` | string | The OpenID Connect private key to use when authentication method is 'private key'. |
| `oidc_required_key` | string | If there is a field in the authentication token response which must be present, enter the name of the field here. |
| `oidc_required_value` | string | If you have specified a Required key, enter the value of the required key here. |
| `oidc_scope` | string | The OpenID Connection OAuth2 scope to request. |
| `oidc_token_endpoint_url` | string | The OpenID Connect token endpoint URL.  This will be loaded from the Metadata URL if provided. |
| `oidc_username_field` | string | The field in the authentication token response to use as the username. |
| `resource_uri` | string | The URI that identifies this resource. |
| `source` | string | The database to query for administrator authentication and authorization. |
