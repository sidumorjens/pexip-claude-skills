# Google OAuth 2.0 Credential

**Endpoint:** `/api/admin/configuration/v1/google_auth_server/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `application_type` | string | The application type of this Google OAuth 2.0 Credential. |
| `client_id` | string | The client ID of this Google OAuth 2.0 Credential. Maximum length: 250 characters. |
| `client_secret` | string | The client secret of this Google OAuth 2.0 Credential. Maximum length: 128 characters. |
| `description` | string | A description of the Google OAuth 2.0 Credential. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `name` | string | The name used to refer to this Google OAuth 2.0 Credential. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
