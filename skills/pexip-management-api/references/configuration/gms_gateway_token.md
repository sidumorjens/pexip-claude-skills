# Google Meet gateway token

**Endpoint:** `/api/admin/configuration/v1/gms_gateway_token/`

## Allowed methods

- **Allowed Methods (list):** GET
- **Allowed Methods (detail):** DELETE, GET, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `certificate` | string | The PEM format TLS certificate. |
| `id` | integer | The primary key. |
| `intermediate_certificate` | string | PEM encoded Google Meet Gateway Intermediate CA Certificate |
| `leaf_certificate` | string | PEM encoded Google Meet Gateway Certificate |
| `private_key` | string | The private key used for the Google Meet gateway token which authenticates your identity in communications between Pexip Infinity and Google Meet. Maximum length: 12288 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `supports_direct_guest_join` | boolean | Indicates if Google Meet Direct Guest Join is supported on this deployment. |
