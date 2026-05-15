# AD FS OAuth 2.0 Client

**Endpoint:** `/api/admin/configuration/v1/adfs_auth_server/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `client_id` | string | The ID of the AD FS OAuth 2.0 Client. Maximum length: 250 characters. |
| `description` | string | A description of the AD FS OAuth 2.0 Client. Maximum length: 250 characters. |
| `federation_service_identifier` | string | The URL which identifies AD FS. Maximum length: 255 characters. |
| `federation_service_name` | string | The FQDN which is used by clients to connect to AD FS. Maximum length: 255 characters. |
| `id` | integer | The primary key. |
| `name` | string | The name used to refer to this AD FS OAuth 2.0 Client. Maximum length: 250 characters. |
| `relying_party_trust_identifier_url` | string | The URL which identifies the OAuth 2.0 resource on AD FS. Maximum length: 255 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
