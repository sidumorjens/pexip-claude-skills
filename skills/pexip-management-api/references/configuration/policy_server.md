# Policy profile

**Endpoint:** `/api/admin/configuration/v1/policy_server/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `description` | string | A description of the policy profile. Maximum length: 250 characters. |
| `enable_avatar_lookup` | boolean | If enabled, requests are sent to the external policy server to fetch avatar images to represent directory contacts and conference participants. |
| `enable_directory_lookup` | boolean | If enabled, requests are sent to the external policy server to fetch directory information (that can be used by some Pexip apps to display a phonebook). |
| `enable_internal_media_location_policy` | boolean | If enabled, the media location configuration based on information from the local database or an external policy server is processed by the local policy script (which may modify the media location configuration). |
| `enable_internal_participant_policy` | boolean | If enabled, the participant configuration based on information from the local database or an external policy server is processed by the local policy script (which may change the participant configuration or cause the call to be rejected). |
| `enable_internal_service_policy` | boolean | If enabled, service configuration retrieved from the local database or an external policy server is processed by the local policy script (which may change the service configuration or cause the call to be rejected). |
| `enable_media_location_lookup` | boolean | If enabled, requests are sent to the external policy server to fetch the system location to use for media allocation. |
| `enable_participant_lookup` | boolean | If enabled, requests are sent to the external policy server to fetch participant configuration data. |
| `enable_registration_lookup` | boolean | If enabled, requests are sent to the external policy server to determine whether a device alias is allowed to register to a Conferencing Node. |
| `enable_service_lookup` | boolean | If enabled, requests are sent to the external policy server to fetch service configuration data (VMRs, Virtual Receptions, Pexip Distributed Gateway calls etc). |
| `id` | integer | The primary key. |
| `internal_media_location_policy_template` | string | A Jinja2 script that takes the existing media location configuration and optionally modifies or overrides location settings. Maximum length: 49152 characters. |
| `internal_participant_policy_template` | string | A Jinja2 script that takes the existing participant configuration and optionally modifies or overrides participant settings. Maximum length: 49152 characters. |
| `internal_service_policy_template` | string | A Jinja2 script that takes the existing service configuration (if any) and optionally modifies or overrides service settings. Maximum length: 49152 characters. |
| `name` | string | The name used to refer to this policy profile. Maximum length: 250 characters. |
| `password` | string | The password used when accessing the policy server. Maximum length: 100 characters. |
| `prefer_local_avatar_configuration` | boolean | If enabled, requests are sent to the Avatar URL configured on the user when looking them up in the directory or viewing their participant avatar in a conference. If no Avatar URL is configured for the user, then the request falls back to the external policy server if enabled. |
| `resource_uri` | string | The URI that identifies this resource. |
| `url` | string | The URL of the external policy server. Maximum length: 255 characters. |
| `username` | string | The username used when accessing the policy server. Maximum length: 100 characters. |
