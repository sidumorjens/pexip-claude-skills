# Certificate signing request

**Endpoint:** `/api/admin/configuration/v1/certificate_signing_request/`

## Allowed methods

- **Allowed Methods (list):** DELETE, GET, POST
- **Allowed Methods (detail):** DELETE, GET, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `ad_compatible` | boolean | Include Microsoft certificate template extension |
| `additional_subject_alt_names` | string | A comma-separated list of subject alternative names to include in the certificate signing request. |
| `certificate` | string | The PEM format TLS certificate. |
| `csr` | string | PEM format certificate signing request data. |
| `dn` | string | The Distinguished Name of the requested certificate's subject. Maximum length: 250 characters. |
| `eku_client_auth` | boolean | Certificate has the clientAuth EKU assigned. |
| `eku_server_auth` | boolean | Certificate has the serverAuth EKU assigned. |
| `id` | integer | The primary key. |
| `private_key` | string | If private_key_type is UPLOAD, the PEM format private key data. Unused otherwise.  Maximum length: 12288 characters. |
| `private_key_passphrase` | string | The passphrase if there are encrypted private keys. |
| `private_key_type` | string | The type of the private key to create (RSA2048, RSA4096, ECDSAP256) or UPLOAD to indicate a user-provided key. |
| `resource_uri` | string | The URI that identifies this resource. |
| `subject_name` | string | The Common Name field of the requested certificate's subject. Maximum length: 250 characters. |
| `tls_certificate` | `tls_certificate` (related resource) | TLS certificate to create a certificate signing request for. |
