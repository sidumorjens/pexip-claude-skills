# NTP server

**Endpoint:** `/api/admin/configuration/v1/ntp_server/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `address` | string | The IP address or FQDN of the NTP server. Maximum length: 255 characters. |
| `description` | string | A description of the NTP server. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `key` | string | This optional field, used in conjunction with the Secure NTP key ID, allows configuration of a SHA1 key for authenticating access to a secure NTP server. Enter the plaintext key; this will be stored as a SHA1 hash. Maximum length: 100 characters. |
| `key_id` | integer | This optional field allows you to configure a key ID which is used in conjunction with the Secure NTP key for authenticating access to a secure NTP server. Range: 1 to 65535. |
| `resource_uri` | string | The URI that identifies this resource. |
