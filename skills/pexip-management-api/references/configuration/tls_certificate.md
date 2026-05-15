# TLS certificate

**Endpoint:** `/api/admin/configuration/v1/tls_certificate/`

## Allowed methods

- **Allowed Methods (list):** DELETE, GET, POST, PATCH
- **Allowed Methods (detail):** DELETE, GET, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `certificate` | string | The PEM formatted certificate. |
| `client_auth_usage` | boolean | Certificate has clientAuth EKU. |
| `end_date` | datetime | The date the certificate is valid until. |
| `id` | integer | The primary key. |
| `issuer_hash` | string | A unique identifier created by hashing the full issuer name. Maximum length: 8 characters. |
| `issuer_key_id` | string | The certificate issuer's key ID. Maximum length: 128 characters. |
| `issuer_name` | string | The Common Name or Organisation field of the certificate's issuer. Maximum 250 characters. |
| `key_id` | string | The certificate's key ID. Maximum length: 128 characters. |
| `nodes` | list | List of nodes (FQDNs) using this TLS certificate |
| `parameters` | string | DH or EC parameters to use with this certificate. |
| `private_key` | string | RSA or ECDSA private key paired with this certificate.  Maximum length: 12288 characters. |
| `private_key_passphrase` | string | The passphrase if there are encrypted private keys. |
| `raw_issuer` | string | The certificate's full issuer name. Maximum length: 250 characters. |
| `raw_subject` | string | The certificate's full subject name. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `serial_no` | string | The certificate's serial number. Maximum length: 128 characters. |
| `server_auth_usage` | boolean | Certificate has serverAuth EKU. |
| `start_date` | datetime | The date the certificate is valid from. |
| `subject_alt_names` | string | Subject alternative names found in the certificate. |
| `subject_hash` | string | A unique identifier created by hashing the full subject name. Maximum length: 8 characters. |
| `subject_name` | string | The Common Name or Organisation field of the certificate's subject. Maximum 250 characters. |
| `text` | string | The information contained in the certificate. |
