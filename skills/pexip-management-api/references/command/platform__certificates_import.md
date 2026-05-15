# /api/admin/command/v1/platform/certificates_import/

**Endpoint:** `/api/admin/command/v1/platform/certificates_import/`

## Allowed methods

- **Allowed Methods (list):** POST

## Fields

| Field | Type | Description |
|---|---|---|
| `bundle` | string | One or more PEM-formatted text files concatenated together, containing any of the following: - trusted CA certificates; - server TLS certificates with matching private keys. DH or EC parameters may follow server TLS certificates. |
| `private_key_passphrase` | string | The passphrase if there are encrypted private keys. |
