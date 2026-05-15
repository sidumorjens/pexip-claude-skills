# Telehealth Profile

**Endpoint:** `/api/admin/configuration/v1/telehealth_profile/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `description` | string | A description of the telehealth profile. Maximum length: 250 characters. |
| `epic_backend_oauth2_app_client_id` | string | The unique OAuth2 application Client ID assigned by Epic for the Pexip Backend application to use when contacting the Epic server.  Maximum length: 255 characters. |
| `epic_backend_oauth2_app_private_key` | string | The private key for the Pexip Backend OAuth2 application to use when authenticating to Epic.  Maximum length: 12288 characters. |
| `epic_backend_oauth2_app_token_endpoint_url` | string | The HTTPS URL of the Epic server's OAuth2 token URL, for example https://epic.example.com/interconnect-aocurprd-oauth/oauth2/token . Maximum length: 255 characters. |
| `epic_encryption_algorithm` | string | The encryption algorithm used by Epic when encrypting telehealth call parameters during telehealth call launch. For Epic releases from August 2019 onwards AES-256-CBC is recommended. |
| `epic_encryption_key` | string | The encryption key used to encrypt and decrypt telehealth parameters passed from Epic to Pexip Infinity when launching calls associated with this Telehealth Integration. Maximum length: 100 characters. |
| `epic_encryption_key_type` | string | The type of the encryption key. 'password': the associated encryption key field contains a simple text password from which a key will be derived, or 'base64key': the associated encryption key field contains a predefined base64-encoded key. If AES-256-CBC is the encryption algorithm used, 'base64key' is mandated. |
| `epic_patient_app_client_id` | string | The unique OAuth2 application Client ID assigned by Epic for the Pexip Telehealth Patient application to use when contacting clients.  Maximum length: 255 characters. |
| `epic_patient_app_client_secret` | string | The unique OAuth2 application Client ID assigned by Epic for the Pexip Telehealth Patient application.  Maximum length: 100 characters. |
| `epic_provider_app_client_id` | string | The unique OAuth2 application Client ID assigned by Epic for the Pexip Telehealth Provider application to use when contacting clients.  Maximum length: 255 characters. |
| `epic_provider_app_client_secret` | string | The unique OAuth2 application Client ID assigned by Epic for the Pexip Telehealth Provider application.  Maximum length: 100 characters. |
| `id` | integer | The primary key. |
| `infinity_webapp_server_base_url` | string | The public base URL for the Pexip web app (such as your public Conferencing Node, Proxying Edge Node, reverse proxy or load balancer), for example: 'https://[infinity deployment]/' .Maximum length: 255 characters. |
| `launch_error_web_template` | string | A template for the error page shown to users if telehealth call launch fails. Maximum length: 12288 characters. |
| `name` | string | The name of the telehealth profile. Maximum length: 250 characters. |
| `patient_alias_template` | string | The jinja2 template used for generating patient aliases used by patients when joining a telehealth conference. This must include the value of {{base_telehealth_alias}} somewhere in the alias, although you can use your own choice of prefix and/or suffix.  Maximum length: 1024 characters. |
| `patient_display_name_template` | string | The jinja2 template used for generating display names used by patients when joining a telehealth conference. Maximum length: 1024 characters. |
| `patient_oauth2_redirect_url` | string | OAuth2 redirect URL for the patient telehealth application, such as 'https://[infinity deployment]/api/telehealth/v1/patient/oauth2authorized/[uuid]'. Maximum length: 255 characters. |
| `patient_web_join_link_template` | string | The jinja2 template used for generating HTTPS web join links used by patients when joining a telehealth conference. This must include the value of {{telehealth_alias}} somewhere in the link (usually as a conference= parameter), and you may customize other aspects of the URI if required.  Maximum length: 1024 characters. |
| `provider_alias_template` | string | The jinja2 template used for generating provider aliases used by providers (e.g. doctors) when joining a telehealth conference. This must include the value of {{base_telehealth_alias}} somewhere in the alias, although you can use your own choice of prefix and/or suffix.  Maximum length: 1024 characters. |
| `provider_display_name_template` | string | The jinja2 template used for generating display names used by providers (e.g. doctors) when joining a telehealth conference. Maximum length: 1024 characters. |
| `provider_oauth2_redirect_url` | string | OAuth2 redirect URL for the provider telehealth application, such as 'https://[infinity deployment]/api/telehealth/v1/provider/oauth2authorized/[uuid]/'. Maximum length: 255 characters. |
| `provider_web_join_link_template` | string | The jinja2 template used for generating HTTPS web join links used by providers (e.g. doctors) when joining a telehealth conference. This must include the value of {{telehealth_alias}} somewhere in the link (usually as a conference=parameter) and the pin parameter, and you may customize other aspects of the URI if required.  Maximum length: 1024 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `service_name_template` | string | The jinja2 template used for generating the telehealth conference VMR name. This must include the value of {{unique_encounter_id}} somewhere in the name, although you can use your own choice of prefix and/or suffix. The name must be the same for all participants who will join; thus if your integration is used for group appointments you must NOT include  {{launch_information.fname}} {{launch_information.lname}} as these will differ from patient to patient. Maximum length: 1024 characters. |
| `telehealth_call_domain` | string | The name of the domain to use for telehealth aliases associated with this telehealth profile location. Maximum length: 255 characters. |
| `telehealth_integration_base_url` | string | The base HTTPS URL of the Epic server. Maximum length: 255 characters. |
| `telehealth_integration_oauth2_base_api_url` | string | The base HTTPS URL of the Epic server's OAuth2 APIs, for example https://epic.example.com/interconnect-aocurprd-oauth . Maximum length: 255 characters. |
| `uuid` | string | Unique identifier for the Telehealth Profile. |
