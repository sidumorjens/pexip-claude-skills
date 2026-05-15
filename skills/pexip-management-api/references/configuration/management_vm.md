# Management Node

**Endpoint:** `/api/admin/configuration/v1/management_vm/`

## Allowed methods

- **Allowed Methods (list):** GET, POST, DELETE
- **Allowed Methods (detail):** GET, POST, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `address` | string | The IPv4 address for this Management Node. |
| `alternative_fqdn` | string | An identity for this Management Node, used by the web interface when indicating its own identity. If configured, the name must match an identity in the Management Node's TLS certificate. Maximum length: 255 characters. |
| `description` | string | A description of the Management Node. Maximum length: 250 characters. |
| `dns_servers` | `dns_server` (related resource) | The DNS servers to be used by this Management Node. |
| `domain` | string | The domain name for this Management Node. Maximum length: 192 characters. |
| `enable_ssh` | string | Allows an administrator to log in to this node over SSH. |
| `event_sinks` | `event_sink` (related resource) | The event sinks to be used by this Management Node. |
| `gateway` | string | The IPv4 address of the default gateway. |
| `hostname` | string | The hostname for this Management Node. Maximum length: 63 characters. |
| `http_proxy` | `http_proxy` (related resource) | The web proxy to be used for outbound web requests from this Management Node. |
| `id` | integer | The primary key. |
| `initializing` | boolean | This Management Node is initializing the configuration file. |
| `ipv6_address` | string | The IPv6 address for this Management Node. |
| `ipv6_gateway` | string | The IPv6 address of the default gateway. If unspecified, the gateway will be configured from IPv6 router advertisements. |
| `mtu` | integer | Maximum Transmission Unit - the size of the largest packet that can be transmitted via the network interface for this system location. It depends on your network topology as to whether you may need to specify an MTU value here. Range: 512 to 1500. |
| `name` | string | The name used to refer to this Management Node. Maximum length: 32 characters. |
| `netmask` | string | The IPv4 network mask for this Management Node. |
| `ntp_servers` | `ntp_server` (related resource) | The NTP servers to be used by this Management Node. |
| `primary` | boolean | The IPv4 address for this Management Node. |
| `resource_uri` | string | The URI that identifies this resource. |
| `secondary_config_passphrase` | string | The passphrase to be used to encrypt the configuration for the new Management Node. |
| `snmp_authentication_password` | string | The password used for SNMPv3 authentication. Minimum length: 8 characters. Maximum length: 100 characters. |
| `snmp_community` | string | The SNMP group to which this virtual machine belongs. Maximum length: 16 characters. |
| `snmp_mode` | string | The SNMP mode. |
| `snmp_network_management_system` | `snmp_network_management_system` (related resource) | The Network Management System to which SNMP traps for the Management Node will be sent. |
| `snmp_privacy_password` | string | The password used for SNMPv3 privacy. Minimum length: 8 characters. Maximum length: 100 characters. |
| `snmp_system_contact` | string | The SNMP contact for this Management Node. Maximum length: 70 characters. |
| `snmp_system_location` | string | The SNMP location for this Management Node. Maximum length: 70 characters. |
| `snmp_username` | string | The username used to authenticate SNMPv3 requests. Maximum length: 100 characters. |
| `ssh_authorized_keys` | `ssh_authorized_key` (related resource) | The selected authorized keys |
| `ssh_authorized_keys_use_cloud` | boolean | Allows use of SSH keys configured in the cloud service. |
| `static_nat_address` | string | The IPv4 static NAT address for this Management Node. |
| `static_routes` | `static_route` (related resource) | Additional configuration to permit routing of traffic to networks not accessible through the configured default gateway. |
| `syslog_servers` | `syslog_server` (related resource) | The Syslog servers to be used by this Management Node. |
| `tls_certificate` | `tls_certificate` (related resource) | The TLS certificate to use on this node. |
| `tls_client_certificate` | `tls_certificate` (related resource) | The TLS certificate to use on this node when responding to client certificate challenges. |
