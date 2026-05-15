# Syslog server

**Endpoint:** `/api/admin/configuration/v1/syslog_server/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `address` | string | The IP address or FQDN of the remote syslog server. Maximum length: 255 characters. |
| `audit_log` | boolean | Enable sending of audit log entries. |
| `description` | string | A description of the Syslog server. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `port` | integer | The port on the remote syslog server. Range: 1 to 65535. Default: 514. |
| `proto_format` | string | The format of the syslog protocol used when sending to the remote syslog server. |
| `resource_uri` | string | The URI that identifies this resource. |
| `support_log` | boolean | Enable sending of support and administrator log entries. |
| `syslog_log` | boolean | Enable sending of system log entries. |
| `transport` | string | The IP transport used to connect to the remote syslog server. |
| `web_log` | boolean | Enable sending of web server log entries. |
