# OAuth2 client

**Endpoint:** `/api/admin/configuration/v1/oauth2_client/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `client_id` | string | The OAuth2 client ID. |
| `client_name` | string | The name of this OAuth2 client. |
| `private_key_jwt` | string | The private key for this OAuth2 client. This is only returned on creation. |
| `resource_uri` | string | The URI that identifies this resource. |
| `role` | `role` (related resource) | The role assigned to this OAuth2 client. |
