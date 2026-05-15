# Conferencing Node

**Endpoint:** `/api/admin/configuration/v1/worker_vm/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `address` | string | The IPv4 address for this Conferencing Node. Each Conferencing Node must have a unique IP address. |
| `alternative_fqdn` | string | (Required for Conferencing Nodes that are involved in signaling of calls to and from Skype for Business servers.) An identity for this Conferencing Node, used in signaling SIP TLS Contact addresses. Maximum length: 255 characters. |
| `cloud_bursting` | boolean | Defines whether this Conference Node is a cloud bursting node |
| `deployment_type` | string | The means by which this Conferencing Node will be deployed. |
| `description` | string | A description of the Conferencing Node. Maximum length: 250 characters. |
| `domain` | string | The domain name for this Conferencing Node. Maximum length: 192 characters. |
| `enable_distributed_database` | boolean | This should usually be True for all nodes which are expected to be 'always on', and False for nodes which are expected to only be powered on some of the time (e.g. cloud bursting nodes that are likely to only be operational during peak times). Avoid frequent toggling of this setting. |
| `enable_ssh` | string | Allows an administrator to log in to this node over SSH. |
| `gateway` | string | The IPv4 address of the default gateway. |
| `hostname` | string | The hostname for this Conferencing Node. Each Conferencing Node must have a unique DNS hostname. Maximum length: 63 characters. |
| `id` | integer | The primary key. |
| `ipv6_address` | string | The IPv6 address for this Conferencing Node. Each Conferencing Node must have a unique IPv6 address. |
| `ipv6_gateway` | string | The IPv6 address of the default gateway. If unspecified, the gateway will be configured from IPv6 router advertisements. |
| `maintenance_mode` | boolean | While maintenance mode is enabled, this Conferencing Node will not accept any new conference instances. |
| `maintenance_mode_reason` | string | A description for the reason we are in maintenance mode. Maximum length: 250 characters. |
| `managed` | boolean | Boolean data. Ex: True |
| `media_priority_weight` | integer | The relative priority of this node, used when determining the order of nodes to which Pexip Infinity will attempt to send media. A higher number represents a higher priority; the default is 0, i.e. the lowest priority. |
| `name` | string | The name used to refer to this Conferencing Node. Each Conferencing Node must have a unique name. Maximum length: 32 characters. |
| `netmask` | string | The IPv4 network mask for this Conferencing Node. |
| `node_type` | string | The role of this Conferencing Node. |
| `password` | string | The password to be used when logging in to this Conferencing Node over SSH. The username will always be admin. |
| `resource_uri` | string | The URI that identifies this resource. |
| `secondary_address` | string | The optional secondary interface IPv4 address for this Conferencing Node. |
| `secondary_netmask` | string | The optional secondary interface network mask for this Conferencing Node. |
| `service_manager` | boolean | Boolean data. Ex: True |
| `service_policy` | boolean | Boolean data. Ex: True |
| `signalling` | boolean | Boolean data. Ex: True |
| `snmp_authentication_password` | string | The password used for SNMPv3 authentication. Minimum length: 8 characters. Maximum length: 100 characters. |
| `snmp_community` | string | The SNMP group to which this virtual machine belongs. Maximum length: 16 characters. |
| `snmp_mode` | string | The SNMP mode. |
| `snmp_privacy_password` | string | The password used for SNMPv3 privacy. Minimum length: 8 characters. Maximum length: 100 characters. |
| `snmp_system_contact` | string | The SNMP contact for this Conferencing Node. Maximum length: 70 characters. |
| `snmp_system_location` | string | The SNMP location for this Conferencing Node. Maximum length: 70 characters. |
| `snmp_username` | string | The username used to authenticate SNMPv3 requests. Maximum length: 100 characters. |
| `ssh_authorized_keys` | `ssh_authorized_key` (related resource) | The selected authorized keys |
| `ssh_authorized_keys_use_cloud` | boolean | Allows use of SSH keys configured in the cloud service. |
| `static_nat_address` | string | The public IPv4 address used by the Conferencing Node when it is located behind a NAT device. Note that if you are using NAT, you must also configure your NAT device to route the Conferencing Node's IPv4 static NAT address to its IPv4 address. |
| `static_routes` | `static_route` (related resource) | Additional configuration to permit routing of traffic to networks not accessible through the configured default gateway. |
| `system_location` | `system_location` (related resource) | The system location for this Conferencing Node. A system location should not contain a mixture of Proxying Edge Nodes and Transcoding Conferencing Nodes. |
| `tls_certificate` | `tls_certificate` (related resource) | The TLS certificate to use on this node. |
| `tls_client_certificate` | `tls_certificate` (related resource) | The TLS certificate to use on this node when responding to SIP/TLS client certificate challenges. |
| `transcoding` | boolean | Deprecated field - use node_type field instead. |
| `vm_cpu_count` | integer | Enter the number of virtual CPUs to assign to this Conferencing Node. We do not recommend that you assign more virtual CPUs than there are physical cores on a single processor on the host server (unless you have enabled NUMA affinity). For example, if the host server has 2 processors each with 12 physical cores, we recommend that you assign no more than 12 virtual CPUs. Range: 2 to 128. Default: 4. |
| `vm_system_memory` | integer | The amount of RAM (in megabytes) to assign to this Conferencing Node. Range: 2000 to 64000. Default: 4096. |
