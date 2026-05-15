# OTJ O365 Graph Integration

**Endpoint:** `/api/admin/configuration/v1/mjx_graph_deployment/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `client_id` | string | The Application (client) ID which was generated when creating an App Registration in Azure Active Directory. |
| `client_secret` | string | The client secret of the application you created in the Azure Portal, for use by OTJ. Maximum length: 100 characters. |
| `description` | string | A description of this OTJ O365 Graph Integration. Maximum length: 250 characters. |
| `disable_proxy` | boolean | Bypass the web proxy (where configured for the system location) for outbound requests sent from this integration. |
| `graph_api_domain` | string | The FQDN to use when connecting to the Graph API. Maximum length: 192 characters. |
| `id` | integer | The primary key. |
| `mjx_integrations` | `mjx_integration` (related resource) | The One-Touch Join Profiles associated with this OTJ O365 Graph Integration. |
| `name` | string | The name of the OTJ O365 Graph Integration. Maximum length: 250 characters. |
| `oauth_token_url` | string | The URI of the OAuth 2.0 (v2) token endpoint. This should be copied from the 'Endpoints' section in Azure Active Directory App Registrations. Maximum length: 255 characters. |
| `request_quota` | integer | The maximum number of API requests that can be made by OTJ to the Microsoft Graph API in a 24-hour period. Minimum number of requests: 10000  Maximum number of requests: 10000000  Default number of requests: 1000000 |
| `resource_uri` | string | The URI that identifies this resource. |
