# SMTP server

**Endpoint:** `/api/admin/configuration/v1/smtp_server/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `address` | string | The IP address or FQDN of the SMTP server. Maximum length: 255 characters. |
| `connection_security` | string | The connection security to use when connecting to this email server. |
| `description` | string | A description of the SMTP server. Maximum length: 250 characters. |
| `from_email_address` | string | The 'From' email address to use when sending emails via this server. This must be an email address that is permitted to be used for sending email using this server and account.  Maximum length: 100 characters. |
| `id` | integer | The primary key. |
| `name` | string | The name used to refer to this SMTP server. Maximum length: 250 characters. |
| `password` | string | The password of a valid account on the SMTP server. Maximum length: 100 characters. |
| `port` | integer | The IP port on the SMTP server to which the Conferencing Node will connect. Range: 1 to 65535. Default: 587. |
| `resource_uri` | string | The URI that identifies this resource. |
| `username` | string | The username of a valid account on the SMTP server. Maximum length: 100 characters. |
