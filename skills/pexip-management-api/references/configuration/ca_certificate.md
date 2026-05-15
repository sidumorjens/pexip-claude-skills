# Trusted CA certificate

**Endpoint:** `/api/admin/configuration/v1/ca_certificate/`

## Allowed methods

- **Allowed Methods (list):** DELETE, GET, POST
- **Allowed Methods (detail):** DELETE, GET, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `certificate` | string | The PEM formatted certificate. |
| `end_date` | datetime | The date the certificate is valid until. |
| `id` | integer | The primary key. |
| `issuer_hash` | string | A unique identifier created by hashing the full issuer name. Maximum length: 8 characters. |
| `issuer_key_id` | string | The certificate issuer's key ID. Maximum length: 128 characters. |
| `issuer_name` | string | The Common Name or Organisation field of the certificate's issuer. Maximum 250 characters. |
| `key_id` | string | The certificate's key ID. Maximum length: 128 characters. |
| `raw_issuer` | string | The certificate's full issuer name. Maximum length: 250 characters. |
| `raw_subject` | string | The certificate's full subject name. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `serial_no` | string | The certificate's serial number. Maximum length: 128 characters. |
| `start_date` | datetime | The date the certificate is valid from. |
| `subject_hash` | string | A unique identifier created by hashing the full subject name. Maximum length: 8 characters. |
| `subject_name` | string | The Common Name or Organisation field of the certificate's subject. Maximum 250 characters. |
| `text` | string | The information contained in the certificate. |
| `trusted_intermediate` | boolean | Allow use of this intermediate certificate for constructing TLS verification chains. |
