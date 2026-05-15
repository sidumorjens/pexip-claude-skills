# Device alias

**Endpoint:** `/api/admin/configuration/v1/device/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `alias` | string | The alias with which the device must register to Pexip Infinity. Maximum length: 250 characters. |
| `creation_time` | datetime | The time at which this device alias was created. |
| `description` | string | A description of the device alias. Note that this description may be displayed to end users on registered Pexip apps who are performing a directory search. Maximum length: 250 characters. |
| `enable_h323` | boolean | Allows a device to register over the H323 protocol, using this alias. |
| `enable_infinity_connect_non_sso` | boolean | Allows a legacy Infinity Connect client to register using this alias. The registration is optionally authenticated using the specified username and password. |
| `enable_infinity_connect_sso` | boolean | Allows a legacy Infinity Connect client to register using this alias, using AD FS to authenticate the registration. |
| `enable_sip` | boolean | Allows a device to register over the SIP protocol, using this alias. |
| `enable_standard_sso` | boolean | Allows a device to register using this alias and authenticate the registration against a SAML or OIDC Identity Provider. |
| `id` | integer | The primary key. |
| `password` | string | The password with which to authenticate the device. The password is case-sensitive. Maximum length: 100 characters. |
| `primary_owner_email_address` | string | The email address of the owner of the device. Maximum length: 100 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `sso_identity_provider_group` | `identity_provider_group` (related resource) | Select the set of Identity Providers which may be used to authenticate with when IdP SSO is enabled. |
| `sync_tag` | string | A unique identifier used to track which LDAP sync template created this device. Maximum length: 250 characters. |
| `tag` | string | A unique identifier used to track usage of this device. Maximum length: 250 characters. |
| `username` | string | The username with which to authenticate the device. The username is case-sensitive. Maximum length: 100 characters. |
