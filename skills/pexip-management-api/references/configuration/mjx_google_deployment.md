# OTJ Google Workspace Integration

**Endpoint:** `/api/admin/configuration/v1/mjx_google_deployment/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `auth_endpoint` | string | The URI of the Google OAuth 2.0 endpoint. Maximum length: 255 characters. |
| `client_email` | string | The email address of the service account (or authorization user account) used by this OTJ Google Workspace Integration when logging in to Google Workspace to read room calendars. Maximum length: 256 characters. |
| `client_id` | string | The client ID of the application you created in the Google API Console, for use by OTJ. Maximum length: 250 characters. |
| `client_secret` | string | The client secret for the application you created in the Google API Console, for use by OTJ. |
| `description` | string | A description of this OTJ Google Workspace Integration. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `maximum_number_of_api_requests` | integer | The maximum number of API requests that can be made by OTJ to your Google Workspace Domain in a 24-hour period. Minimum number of requests: 10000  Default number of requests: 900000 |
| `mjx_integrations` | `mjx_integration` (related resource) | The OTJ Google Workspace Integration associated with this One-Touch Join Profile. |
| `name` | string | The name of the OTJ Google Workspace Integration. Maximum length: 250 characters. |
| `oauth_state` | string | A unique state which is used during the OAuth sign-in flow. |
| `private_key` | string | The private key used by OTJ to authenticate the service account when logging in to Google Workspace to read the room calendars. Maximum length: 12288 characters. |
| `redirect_uri` | string | The redirect URI you configured in the Google API Console Credentials. It must be in the format 'https://[Management Node Address]/admin/platform/mjxgoogledeployment/oauth_redirect/'. Maximum length: 255 characters. |
| `refresh_token` | string | The OAuth refresh token which is obtained after successfully finishing the authorization for accessing Google API flow. Maximum length: 4096 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `token_endpoint` | string | The URI of the Google authorization server. Maximum length: 255 characters. |
| `use_user_consent` | boolean | Leave this option disabled to use the recommended method of a service account to access room calendars. Enable this option to use an authorization user, authenticated via OAuth, to access room calendars. |
