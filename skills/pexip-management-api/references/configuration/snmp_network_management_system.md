# SNMP Network Management System

**Endpoint:** `/api/admin/configuration/v1/snmp_network_management_system/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `address` | string | The IP address or FQDN of the SNMP Network Management System. Maximum length: 255 characters. |
| `description` | string | A description of the SNMP Network Management System. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `name` | string | The name used to refer to this SNMP Network Management System. Maximum length: 250 characters. |
| `port` | integer | The SNMP port of the Network Management System. Range: 1 to 65535. Default: 161. |
| `resource_uri` | string | The URI that identifies this resource. |
| `snmp_trap_community` | string | The SNMP trap community name. Maximum length: 16 characters. |
