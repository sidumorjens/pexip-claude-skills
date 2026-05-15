# OTJ Exchange Integration

**Endpoint:** `/api/admin/configuration/v1/mjx_exchange_deployment/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `authentication_method` | string | The method used to authenticate to Exchange. |
| `autodiscover_urls` | `mjx_exchange_autodiscover_url` (related resource) | The Autodiscover URLs associated with this One-Touch Join Exchange Integration. |
| `description` | string | An optional description of this One-Touch Join Exchange Integration. Maximum length: 250 characters. |
| `disable_proxy` | boolean | Bypass the web proxy (where configured for the system location) for outbound requests sent from this integration. |
| `ews_url` | string | The URL used to connect to Exchange Web Services (EWS) on the Exchange server. Maximum length: 255 characters. |
| `find_items_request_quota` | integer | The number of Find Item requests that can be made by OTJ to your Exchange Server in a 24-hour period. Minimum number of requests: 10000  Maximum number of requests: 10000000  Default number of requests: 1000000 |
| `id` | integer | The primary key. |
| `kerberos_auth_every_request` | boolean | When Kerberos authentication is enabled, send a Kerberos Authorization header in every request to the Exchange server. |
| `kerberos_enable_tls` | boolean | If enabled, all communication to the KDC will go through an HTTPS proxy and all traffic to the KDC will be encrypted using TLS. |
| `kerberos_exchange_spn` | string | The Exchange Service Principal Name (SPN). Maximum length: 255 characters. |
| `kerberos_kdc` | string | The address of the Kerberos key distribution center (KDC). Maximum length: 255 characters. |
| `kerberos_kdc_https_proxy` | string | The URL of the Kerberos key distribution center (KDC) HTTPS proxy. Maximum length: 255 characters. |
| `kerberos_realm` | string | The Kerberos Realm, which is usually your domain in upper-case. Maximum length: 250 characters. |
| `kerberos_verify_tls_using_custom_ca` | boolean | If enabled, use the configured Root Trust CA Certificates to verify the KDC HTTPS proxy SSL certificate. If disabled, the HTTPS proxy SSL certificate is verified using the system-wide default set of trusted certificates. |
| `mjx_integrations` | `mjx_integration` (related resource) | The One-Touch Join Profiles associated with this OTJ Exchange Integration. |
| `name` | string | The name of this One-Touch Join Exchange Integration. Maximum length: 250 characters. |
| `oauth_auth_endpoint` | string | The URI of the OAuth authorization endpoint. This should be copied from the 'Endpoints' section in Azure Active Directory App Registrations. Maximum length: 255 characters. |
| `oauth_client_id` | string | The Application ID which was generated when creating an App Registration in Azure Active Directory. |
| `oauth_redirect_uri` | string | The redirect URI you entered when creating an App Registration in Azure Active Directory. It should be in the format 'https://[Management Node Address]/admin/platform/mjxexchangedeployment/oauth_redirect/'. Maximum length: 255 characters. |
| `oauth_refresh_token` | string | The OAuth refresh token which is obtained after successfully signing in via the OAuth flow. Maximum length: 4096 characters. |
| `oauth_state` | string | A unique state which is used during the OAuth sign-in flow. |
| `oauth_token_endpoint` | string | The URI of the OAuth token endpoint. This should be copied from the 'Endpoints' section in Azure Active Directory App Registrations. Maximum length: 255 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `service_account_password` | string | The password of the service account to be used by the One-Touch Join Exchange Integration. Maximum length: 100 characters. |
| `service_account_username` | string | The username of the service account to be used by the One-Touch Join Exchange Integration. Maximum length: 100 characters. |
