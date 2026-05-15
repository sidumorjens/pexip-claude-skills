# Identity Provider

**Endpoint:** `/api/admin/configuration/v1/identity_provider/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `assertion_consumer_service_url` | string | A URL that can be used in the authentication process with this Identity Provider. For SAML2 this should be in the format https://<webapp_FQDN>/api/v1/samlconsumer/<uuid> and for OpenID Connect https://<webapp_FQDN>/api/v1/oidcconsumer/<uuid>. <webapp_FQDN> is the FQDN from which the web app is accessed, and <uuid> is the UUID shown in the field above. You should add one redirect URL for every web app FQDN in your deployment. Maximum length: 255 characters. |
| `assertion_consumer_service_url10` | string | Enter any additional redirect URLs valid for use with this Identity Provider. Maximum length: 255 characters. |
| `assertion_consumer_service_url2` | string | Enter any additional redirect URLs valid for use with this Identity Provider. Maximum length: 255 characters. |
| `assertion_consumer_service_url3` | string | Enter any additional redirect URLs valid for use with this Identity Provider. Maximum length: 255 characters. |
| `assertion_consumer_service_url4` | string | Enter any additional redirect URLs valid for use with this Identity Provider. Maximum length: 255 characters. |
| `assertion_consumer_service_url5` | string | Enter any additional redirect URLs valid for use with this Identity Provider. Maximum length: 255 characters. |
| `assertion_consumer_service_url6` | string | Enter any additional redirect URLs valid for use with this Identity Provider. Maximum length: 255 characters. |
| `assertion_consumer_service_url7` | string | Enter any additional redirect URLs valid for use with this Identity Provider. Maximum length: 255 characters. |
| `assertion_consumer_service_url8` | string | Enter any additional redirect URLs valid for use with this Identity Provider. Maximum length: 255 characters. |
| `assertion_consumer_service_url9` | string | Enter any additional redirect URLs valid for use with this Identity Provider. Maximum length: 255 characters. |
| `attributes` | `identity_provider_attribute` (related resource) | Select the attributes used by this Identity Provider. |
| `description` | string | A description of the Identity Provider. Maximum length: 250 characters. |
| `digest_algorithm` | string | Digest algorithm used to sign SAML authentication request messages and service metadata |
| `disable_popup_flow` | boolean | Disable pop-up windows used during Single Sign On |
| `display_name_attribute_name` | string | The SAML 2.0 attribute name from which the user's display name will be extracted. If one is not specified, participants are able to enter their own display name. Default: NameId. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `idp_entity_id` | string | The identifier for this Identity Provider integration. For SAML IdPs this is the Entity ID and for OpenID Connect IdPs this is the Issuer for returned JWTs.  Maximum length: 250 characters. |
| `idp_public_key` | string | The public key used  to verify assertions signed by this Identity Provider. Maximum length: 4096 characters. |
| `idp_type` | string | Select the protocol used by this Identity Provider. |
| `name` | string | The name used to refer to this Identity Provider. This name will be visible to end users, so you should use a name that will help users differentiate between Identity Providers without compromising security. Maximum length: 250 characters. |
| `oidc_additional_scopes` | string | Space-separated list of additional scopes to request from the OpenID Connect Identity Provider. Maximum length: 250 characters. |
| `oidc_client_id` | string | The client identifier provided by the OpenID Connect Identity Provider. Maximum length: 250 characters. |
| `oidc_client_secret` | string | The client secret provided by the OpenID Connect Identity Provider. Maximum length: 100 characters. |
| `oidc_display_name_claim_name` | string | The claim name from which the user's display name will be extracted. This can come from either the JWT, or data from the UserInfo endpoint (if one is configured). Maximum length: 250 characters. |
| `oidc_flow` | string | The flow used by the OpenID Connect Identity Provider. |
| `oidc_france_connect_required_eidas_level` | string | The eIDAS level to use in requests and responses. This should not be changed from the default "Disabled" unless advised by your Pexip support representative. |
| `oidc_jwks_url` | string | Download location for your Identity Provider's JSON Web Key Set (JWKS) to enable signature verification. Not required when using HS256 signatures. Maximum length: 255 characters. |
| `oidc_registration_alias_claim_name` | string | The claim name from which the user's registration alias will be extracted. This can come from either the JWT, or data from the UserInfo endpoint (if one is configured). Maximum length: 250 characters. |
| `oidc_token_endpoint_auth_scheme` | string | The authentication method used by Infinity to authenticate when using the token endpoint. |
| `oidc_token_signature_scheme` | string | The algorithm used by the Identity Provider to sign the contents of the token. |
| `oidc_token_url` | string | OpenID Connect Token Endpoint URL used for exchanging codes for tokens in the Authorization Code Flow. Not required when using the Implicit Flow. Maximum length: 255 characters. |
| `oidc_user_info_url` | string | You can optionally enter here the URL of an OpenID Connect UserInfo Endpoint if you wish to use this to retrieve informtion about the user. Maximum length: 255 characters. |
| `registration_alias_attribute_name` | string | The SAML 2.0 attribute name from which the user's registration alias will be extracted. If one is not specified, the user will not be able to register. Default: NameId. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `service_entity_id` | string | The Entity ID for this SAML service. Maximum length: 250 characters. |
| `service_private_key` | string | Private key used by Pexip Infinity when communicating with the Identity Provider. Maximum length: 12288 characters. |
| `service_public_key` | string | Public key used by Pexip Infinity when communicating with the Identity Provider. This must be in PEM (certificate) format. Maximum length: 4096 characters. |
| `signature_algorithm` | string | Signature algorithm used to sign SAML authentication request messages and service metadata |
| `sso_url` | string | The URL to which users are sent when authenticating with this Identity Provider. Custom query string parameters may be appended, e.g. https://<url>?foo=bar. Maximum length: 255 characters. |
| `uuid` | string | A unique identifier for the Identity Provider configuration. A value is automatically assigned and there is normally no need to modify it. |
| `worker_fqdn_acs_urls` | boolean | Automatically generate allowed redirect URLs from the configured FQDNs for each Conferencing Node. |
