# Google Meet access token

**Endpoint:** `/api/admin/configuration/v1/gms_access_token/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `id` | integer | The primary key. |
| `name` | string | The name used to refer to this Google Meet access token. These tokens should be associated with any Virtual Receptions and Call Routing Rules that you configure to handle Google Meet meetings. Maximum length: 32 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `token` | string | The access token that identifies and authenticates your Google Workspace account in communications between Pexip Infinity and Google Meet. Maximum length: 100 characters. |
