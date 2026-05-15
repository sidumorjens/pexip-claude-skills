# System location

**Endpoint:** `/api/admin/configuration/v1/system_location/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `bdpm_pin_checks_enabled` | string | Select this option to instruct Pexip Infinity's Break-in Defense Policy Manager to temporarily block all access to a VMR that receives a significant number of incorrect PIN entry attempts (and thus may perhaps be under attack from a malicious actor). By default, this will block ALL new access attempts to a VMR for up to 10 minutes if more than 20 incorrect PIN entry attempts are made against that VMR in a 10 minute window. Note: this provides a measure of resistance against PIN cracking attacks, but it is not a substitute for having a long PIN (6 digits or longer recommended) and it will not protect against a determined and patient - or lucky - attacker. Also, enabling this feature could potentially allow a malicious attacker or a legitimate user with incorrect access details to prevent legitimate access to VMRs or other call services for a period. This setting is applied according to the location of the node that receives the call signaling. |
| `bdpm_scan_quarantine_enabled` | string | Select this option to instruct Pexip Infinity's Break-in Defense Policy Manager to temporarily block service access attempts from any source IP address that dials a significant number of incorrect aliases in a short period (and thus may perhaps be attempting to scan your deployment to discover valid aliases to allow the attacker to make improper use of VMRs or gateway rules - such as toll fraud attempts). By default, this will block ALL new call service access attempts from an IP address if more than 20 incorrect aliases are dialed from that IP address over SIP, H.323 or WebRTC (Pexip apps) in a 10 minute window. Note: this provides a measure of resistance against scanners such as sipvicious which are sometimes used during toll-fraud attempts, but it will not defend against a determined and patient - or lucky - attacker. Also, enabling this feature could potentially allow a malicious attacker or a legitimate user with incorrect access details to prevent legitimate access to VMRs or other call services for a period, if for example, those users are behind the same firewall as other legitimate users. This setting is applied according to the location of the node that receives the call signaling. |
| `client_stun_servers` | `stun_server` (related resource) | The STUN servers to be used by WebRTC-based Pexip apps when they connect to a Conferencing Node in this location. |
| `client_turn_servers` | `turn_server` (related resource) | The TURN servers to be used by WebRTC-based Pexip apps when they connect to a Conferencing Node in this location. |
| `description` | string | A description of the system location. Maximum length: 250 characters. |
| `dns_servers` | `dns_server` (related resource) | The DNS servers to be used by Conferencing Nodes deployed in this Location. |
| `event_sinks` | `event_sink` (related resource) | The event sinks to be used by Conferencing Nodes deployed in this Location. |
| `h323_gatekeeper` | `h323_gatekeeper` (related resource) | The H.323 gatekeeper to be used for outbound calls from this location. |
| `http_proxy` | `http_proxy` (related resource) | The web proxy to be used for outbound web requests from Conferencing Nodes deployed in this Location. |
| `id` | integer | The primary key. |
| `live_captions_dial_out_1` | `system_location` (related resource) | Dial out routes to live captions service. |
| `live_captions_dial_out_2` | `system_location` (related resource) | Dial out routes to live captions service. |
| `live_captions_dial_out_3` | `system_location` (related resource) | Dial out routes to live captions service. |
| `local_mssip_domain` | string | The name of the SIP domain that is routed from Skype for Business to Pexip Infinity, either as a static route or via federation. It is also used as the default domain in the From address for outgoing SIP gateway calls and outbound SIP calls from conferences without a valid SIP URI as an alias. Maximum length: 255 characters. |
| `media_qos` | integer | The DSCP value for media traffic sent from Conferencing Nodes in this system location. This is an optional setting used to prioritize different types of traffic in large, complex networks. Range: 0 to 63. |
| `mssip_proxy` | `mssip_proxy` (related resource) | The Skype for Business server to use for outbound calls from this location. |
| `mtu` | integer | Maximum Transmission Unit - the size of the largest packet that can be transmitted via the network interface for this system location. It depends on your network topology as to whether you may need to specify an MTU value here. Range: 512 to 1500. |
| `name` | string | The name used to refer to this system location. Maximum length: 250 characters. |
| `ntp_servers` | `ntp_server` (related resource) | The NTP servers to be used by Conferencing Nodes deployed in this Location. |
| `overflow_location1` | `system_location` (related resource) | The system location to handle media when capacity is reached in the current location. |
| `overflow_location2` | `system_location` (related resource) | The system location to handle media when capacity is reached in both the current location and the primary overflow location. |
| `policy_server` | `policy_server` (related resource) | The policy profile to be used by Conferencing Nodes deployed in this Location. |
| `resource_uri` | string | The URI that identifies this resource. |
| `signalling_qos` | integer | The DSCP value for signaling traffic sent from Conferencing Nodes in this system location. This is an optional setting used to prioritize different types of traffic in large, complex networks. Range: 0 to 63. |
| `sip_proxy` | `sip_proxy` (related resource) | The SIP proxy to be used for outbound calls from this location. |
| `snmp_network_management_system` | `snmp_network_management_system` (related resource) | The Network Management System to which SNMP traps for all Conferencing Nodes in this location will be sent. |
| `stun_server` | `stun_server` (related resource) | The STUN server to use by Conferencing Nodes in this location to determine the public IP address to signal to ICE clients (including WebRTC-based Pexip apps) located outside the firewall. |
| `syslog_servers` | `syslog_server` (related resource) | The Syslog servers to be used by Conferencing Nodes deployed in this Location. |
| `teams_proxy` | `teams_proxy` (related resource) | The Teams Connector to use for outbound calls to Microsoft Teams meetings from this location. |
| `transcoding_location` | `system_location` (related resource) | The system location to handle media transcoding for calls (signaling) received in, or sent from, this location. For calls received on a Proxying Edge Node, the media connection with the calling device is handled by a proxying node in this location, and the media is forwarded to a Transcoding Conferencing Node in the nominated Transcoding location. For calls received on a Transcoding Conferencing Node, the media connection with the calling device and the transcoding is handled by a Transcoding Conferencing Node in the nominated Transcoding location. |
| `turn_server` | `turn_server` (related resource) | The TURN server to use when ICE clients (including WebRTC-based Pexip apps) located outside the firewall connect to a Conferencing Node in this location. |
| `use_relay_candidates_only` | boolean | Select this option to force the WebRTC client to route its media through one of the specified client TURN servers. |
