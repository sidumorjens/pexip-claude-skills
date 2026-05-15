# Global settings

**Endpoint:** `/api/admin/configuration/v1/global/`

## Allowed methods

- **Allowed Methods (list):** GET
- **Allowed Methods (detail):** GET, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `aws_access_key` | string | The Amazon Web Services access key ID for the AWS user that the Pexip Infinity Management Node will use to log in to AWS and start and stop the node instances.  Maximum length: 40 characters. |
| `aws_secret_key` | string | The Amazon Web Services secret access key that is associated with the AWS access key ID. |
| `azure_client_id` | string | The ID used to identify the client (sometimes referred to as Application ID). |
| `azure_secret` | string | The Azure secret key that is associated with the Azure client ID. |
| `azure_subscription_id` | string | The ID of an Azure subscription. |
| `azure_tenant` | string | The Azure tenant ID that is associated with the Azure client ID. |
| `bdpm_max_pin_failures_per_window` | integer | Sets the maximum number of PIN failures per service (e.g. VMR) in any sliding 10 minute windowed period, that are allowed from participants at unknown source addresses, before protective action is taken for that service. Range: 5 to 200. |
| `bdpm_max_scan_attempts_per_window` | integer | Sets the maximum number of incorrect alias dial attempts in any sliding 10-minute windowed period, that are allowed from an unknown source address, before protective action is taken against that address. Range: 5 to 200. |
| `bdpm_pin_checks_enabled` | boolean | Select this option to instruct Pexip Infinity's Break-in Defense Policy Manager to temporarily block all access to a VMR that receives a significant number of incorrect PIN entry attempts (and thus may perhaps be under attack from a malicious actor). By default, this will block ALL new access attempts to a VMR for up to 10 minutes if more than 20 incorrect PIN entry attempts are made against that VMR in a 10 minute window. Note: this provides a measure of resistance against PIN cracking attacks, but it is not a substitute for having a long PIN (6 digits or longer recommended) and it will not protect against a determined and patient - or lucky - attacker. Also, enabling this feature could potentially allow a malicious attacker or a legitimate user with incorrect access details to prevent legitimate access to VMRs or other call services for a period. You can also configure this setting on a per-location basis. |
| `bdpm_scan_quarantine_enabled` | boolean | Select this option to instruct Pexip Infinity's Break-in Defense Policy Manager to temporarily block service access attempts from any source IP address that dials a significant number of incorrect aliases in a short period (and thus may perhaps be attempting to scan your deployment to discover valid aliases to allow the attacker to make improper use of VMRs or gateway rules - such as toll fraud attempts). By default, this will block ALL new call service access attempts from an IP address if more than 20 incorrect aliases are dialed from that IP address over SIP, H.323 or WebRTC (Pexip app) in a 10 minute window. Note: this provides a measure of resistance against scanners such as sipvicious which are sometimes used during toll-fraud attempts, but it will not defend against a determined and patient - or lucky - attacker. Also, enabling this feature could potentially allow a malicious attacker or a legitimate user with incorrect access details to prevent legitimate access to VMRs or other call services for a period, if for example, those users are behind the same firewall as other legitimate users. You can also configure this setting on a per-location basis. |
| `bursting_enabled` | boolean | Select this option to instruct Pexip Infinity to monitor the system locations and start up / shutdown overflow Conferencing Nodes hosted in either Amazon Web Services (AWS) or Microsoft Azure when in need of extra capacity. For more information, see the Admin Guide section 'Dynamic bursting to a cloud service'. |
| `bursting_min_lifetime` | integer | The minimum number of minutes that a cloud bursting node is kept powered on. This is because some cloud providers charge by the hour, so when a node is started up it is more efficient to leave it running for 50 minutes — even if it is never used — as that capacity can remain on immediate standby for no extra cost. Note that newly started cloud Conferencing Nodes can take up to 5 minutes to fully startup. Minimum: 5 |
| `bursting_threshold` | integer | The bursting threshold controls when your overflow Conferencing Nodes in the cloud are automatically started up so that they can provide additional conferencing capacity. When the number of additional HD calls that can still be hosted in a location reaches or drops below the threshold, it triggers Pexip Infinity into starting up an overflow node in the overflow location. Note that newly started cloud Conferencing Nodes can take up to 5 minutes to fully startup. Therefore you should set the threshold high enough to ensure that there is enough capacity for incoming calls until the cloud Conferencing Node is available, but not too high so as to start up your cloud nodes unnecessarily and incur extra costs. For more information, see the Administrator Guide section 'Configuring the bursting threshold'.  Minimum: 1 |
| `cloud_provider` | string | Choose the cloud service provider to use for bursting. |
| `contact_email_address` | string | An email address to be added to incident reports to allow Pexip to contact the system administrator for further information. Maximum length: 100 characters. |
| `content_security_policy_header` | string | HTTP Content-Security-Policy header contents for Conferencing Nodes. Maximum length: 4096 characters. |
| `content_security_policy_state` | boolean | Enable HTTP Content-Security-Policy for Conferencing Nodes. |
| `crypto_mode` | string | Controls the media encryption requirements for participants connecting to Pexip Infinity services. Required: All participants (including RTMP participants) must use media encryption. Best effort: Each participant will use media encryption if their device supports it, otherwise the connection will be unencrypted. No encryption: All H.323, SIP and MS-SIP participants must use unencrypted media. (RTMP participants will use encryption if their device supports it, otherwise the connection will be unencrypted.) You can override this global setting for each individual service (VMR, Call Routing Rule etc). |
| `default_theme` | `ivr_theme` (related resource) | The theme to use for services that have no specific theme selected. |
| `default_to_new_webapp` | boolean | Deprecated field - use default_webapp field instead. |
| `default_webapp` | string | Deprecated field - use default_webapp_alias field instead. |
| `default_webapp_alias` | `webapp_alias` (related resource) | The web app path to use by default on conferencing nodes. |
| `deployment_uuid` | string | The ID of the deployment. |
| `disabled_codecs` | `disabled_codec` (related resource) | Choose codecs to disable. |
| `eject_last_participant_backstop_timeout` | integer | The length of time (in seconds) for which a conference will continue with only one participant remaining (independent of Host/Guest role). The time can be configured to values between 60 seconds and 86400 (1 day), or to 0 (never eject). Range: 0 to 86400. Default: 0 (never eject). |
| `enable_analytics` | boolean | Select this option to allow submission of deployment and usage statistics to Pexip. This will help us improve the product. |
| `enable_application_api` | boolean | Enable or disable support for Pexip Infinity Client API. This is required for integration with Pexip's browser-based, desktop and mobile apps, and any other third-party applications that use the client API, as well as for integration with Microsoft Teams. |
| `enable_breakout_rooms` | boolean | Enable the Breakout Rooms feature on VMRs. |
| `enable_chat` | boolean | Enables relay of chat messages between conference participants using supported clients such as the Pexip apps. You can also configure this setting on individual Virtual Meeting Rooms and Virtual Auditoriums. |
| `enable_clock` | boolean | Enables support for displaying an in-conference timer or countdown clock. |
| `enable_denoise` | boolean | Enable server side denoising for speech from noisy participants (see documentation for ways to enable it for a VMR) |
| `enable_dialout` | boolean | Enables calls via the Distributed Gateway, and allows users of Pexip apps and the Pexip management web interface to add participants to a conference. |
| `enable_directory` | boolean | When disabled, Pexip apps will display aliases from their own call history only. When enabled, registered Pexip apps will additionally display the aliases of VMRs, Virtual Auditoriums, Virtual Receptions, and devices registered to the Pexip Infinity deployment. |
| `enable_edge_non_mesh` | boolean | Enable the restricted IPsec network routing requirements of Proxying Edge Nodes. When enabled, if a location only contains Proxying Edge Nodes, then those nodes only require IPsec connectivity with other nodes in that location, the transcoding location, the primary and secondary overflow locations, and with the Management Node. |
| `enable_fecc` | boolean | Enables Pexip apps and SIP/H.323 endpoints to send Far-End Camera Control (FECC) signals to supporting endpoints, in order to pan, tilt and zoom the device's camera. |
| `enable_h323` | boolean | Enable the H323 protocol on all Conferencing Nodes. |
| `enable_legacy_dialout_api` | boolean | Enables outbound calls from a VMR using the legacy dialout API. When disabled, outbound calls are only permitted by following Call Routing Rules. |
| `enable_lync_auto_escalate` | boolean | Determines whether a Skype for Business audio call is automatically escalated so that it receives video from a conference. |
| `enable_lync_vbss` | boolean | Determines whether Video-based Screen Sharing (VbSS) is enabled for Skype for Business calls. |
| `enable_mlvad` | boolean | Enable Voice Focus for advanced voice activity detection. |
| `enable_multiscreen` | boolean | This field is deprecated and will be ignored. |
| `enable_push_notifications` | boolean | This field is deprecated and will be ignored. |
| `enable_rtmp` | boolean | Enables RTMP calls on all Conferencing Nodes. This allows Pexip apps that use RTMP (such as Internet Explorer and Safari versions 6-10 browsers) to access Pexip Infinity services, and allows conference content to be output to streaming and recording services. |
| `enable_sip` | boolean | Enable the SIP protocol over TCP and TLS on all Conferencing Nodes. |
| `enable_sip_udp` | boolean | Enable incoming calls using the SIP protocol over UDP on all Conferencing Nodes. If changing from enabled to disabled, all Conferencing Nodes must be rebooted. |
| `enable_softmute` | boolean | Enable Softmute for advance speech-aware audio gating (see documentation for ways to enable it for a VMR). Note that this does not remove any noise from the audio. |
| `enable_ssh` | boolean | Allows an administrator to log in to the Management and Conferencing Nodes over SSH. This setting can be overridden on individual nodes. |
| `enable_turn_443` | boolean | Enable media relay on TCP port 443 for WebRTC clients as a fallback. |
| `enable_webrtc` | boolean | Enables WebRTC calls on all Conferencing Nodes. This allows access to Pexip Infinity services from Pexip apps that use WebRTC. This includes access via Google Chrome, Microsoft Edge, Firefox, Opera and Safari (version 11 onwards) browsers, and the Pexip app for Windows. |
| `error_reporting_enabled` | boolean | Select this option to permit submission of incident reports. |
| `error_reporting_url` | string | The URL to which incident reports will be sent. Maximum length: 255 characters. |
| `es_connection_timeout` | integer | Maximum number of seconds allowed to connect, send, and wait for a response. |
| `es_initial_retry_backoff` | integer | Initial time, in seconds, for the first retry attempt when an event cannot be delivered. |
| `es_maximum_deferred_posts` | integer | This field is deprecated and will be ignored. |
| `es_maximum_retry_backoff` | integer | Maximum number of seconds allowed for the retry backoff before raising an alarm and stopping the event publisher. |
| `es_media_streams_wait` | integer | Maximum time, in seconds, to wait for an end-of-call media stream message. |
| `es_metrics_update_interval` | integer | Time between metrics updates. To disable eventsink metrics, enter 0. |
| `es_short_term_memory_expiration` | integer | Internal cache expiration time in seconds. Used to briefly store 'participant_disconnected' events in order to gather end-of-call media statistics. |
| `external_participant_avatar_lookup` | boolean | Determines whether or not avatars for external participants will be retrieved using the method appropriate for the external meeting type. |
| `gcp_client_email` | string | The GCP service account ID. |
| `gcp_private_key` | string | The private key for the Google Cloud Platform service account user that the Pexip Infinity Management Node will use to log in to GCP and start and stop the node instances.  Maximum length: 12288 characters. |
| `gcp_project_id` | string | The ID of the GCP project containing bursting nodes. |
| `guests_only_timeout` | integer | The length of time (in seconds) for which a conference will continue with only Guest participants, after all Host participants have left. Range: 0 to 86400. Default: 60. |
| `id` | integer | The primary key. |
| `legacy_api_http` | boolean | This field is deprecated and will be ignored. |
| `legacy_api_password` | string | The password presented to Pexip Infinity by external systems attempting to authenticate with it. Maximum length: 100 characters. |
| `legacy_api_username` | string | The username presented to Pexip Infinity by external systems attempting to authenticate with it. Maximum length: 100 characters. |
| `live_captions_api_gateway` | string | Deprecated field - use /api/admin/configuration/v1/media_processing_server/ instead. |
| `live_captions_app_id` | string | Deprecated field - use /api/admin/configuration/v1/media_processing_server/ instead. |
| `live_captions_enabled` | boolean | Deprecated field - use /api/admin/configuration/v1/media_processing_server/ instead. |
| `live_captions_public_jwt_key` | string | Deprecated field - use /api/admin/configuration/v1/media_processing_server/ instead. |
| `live_captions_vmr_default` | boolean | This option controls whether live captions are enabled by default on all VMRs, Virtual Auditoriums and Call Routing Rules. You can override this setting on each service individually. |
| `liveview_show_conferences` | boolean | Whether to show conferences and backplanes in Live View. |
| `local_mssip_domain` | string | The name of the SIP domain that is routed from Skype for Business to Pexip Infinity, either as a static route or via federation. It is also used as the default domain in the From address for outgoing SIP gateway calls and outbound SIP calls from conferences without a valid SIP URI as an alias. You can also configure a per-location override. Maximum length: 255 characters. |
| `logon_banner` | string | Text of the message to display on the login page of the Pexip Infinity administrator web interface. Maximum length: 4096 characters. |
| `logs_max_age` | integer | The maximum number of days of logs and call history to retain on Pexip nodes. 0 to disable. Logs may be rotated before this time due to limited disk space. Range: 0 to 3650 days. Default: 0 (disabled). |
| `management_qos` | integer | The DSCP value for management traffic sent from the Management Node and Conferencing Nodes. This is an optional setting used to prioritize different types of traffic in large, complex networks. Range: 0 to 63. |
| `management_session_timeout` | integer | The number of minutes a browser session may remain idle before the user is logged out of the Management Node administration interface. Range: 5 to 1440. Default: 30 minutes. |
| `management_start_page` | string | The first page you see after logging into the Management Web. |
| `max_callrate_in` | integer | This optional field allows you to limit the bandwidth of media being received by Pexip Infinity from individual participants, for calls where bandwidth limits have not otherwise been specified. Range: 128 to 8192. |
| `max_callrate_out` | integer | This optional field allows you to limit the bandwidth of media being sent by Pexip Infinity to individual participants, for calls where bandwidth limits have not otherwise been specified. Range: 128 to 8192. Default: 4128. |
| `max_pixels_per_second` | string | Sets the maximum call quality for participants connecting to Pexip Infinity services (VMRs, gateway calls etc.). You can also override this setting on individual services and call routing rules. |
| `max_presentation_bandwidth_ratio` | integer | The maximum percentage of call bandwidth to be allocated to sending presentation. Range: 25 to 75. Default: 75. |
| `media_ports_end` | integer | The end value for the range of ports (UDP and TCP) that all Conferencing Nodes will use to send media (for all call protocols). The media port range must contain at least 100 ports. Range: 10000 to 49999. Default: 49999. |
| `media_ports_start` | integer | The start value for the range of ports (UDP and TCP) that all Conferencing Nodes will use to send media (for all call protocols). The media port range must contain at least 100 ports. Range: 10000 to 49999. Default: 40000. |
| `min_pin_length` | integer | The minimum allowed PIN length for hosts and guests in Virtual Meeting Roomsor Virtual Auditoriums which have PINs configured. Length: 4-20 digits, including any terminal #. |
| `ocsp_responder_url` | string | The URL to which OCSP requests will be sent either if the OCSP state is set to Override, or if the OCSP state is set to On but there is no  URL specified in the TLS certificate. Maximum length: 255 characters. |
| `ocsp_state` | string | Whether to use OCSP when checking the validity of TLS certificates. On: An OCSP request will be sent to the URL specified in the TLS certificate. Override: An OCSP request will be sent to the URL specified in the OCSP responder URL field. |
| `pin_entry_timeout` | integer | The length of time (in seconds) for which a participant will be permitted to remain at the PIN entry screen before being disconnected. Range: 30 to 86400. Default: 120. |
| `pss_customer_id` | string | This field is deprecated and will be ignored. |
| `pss_enabled` | boolean | This field is deprecated and will be ignored. |
| `pss_gateway` | string | This field is deprecated and will be ignored. |
| `pss_token` | string | This field is deprecated and will be ignored. |
| `resource_uri` | string | The URI that identifies this resource. |
| `session_timeout_enabled` | boolean | Determines whether inactive users are automatically logged out of the Management Node administration interface after a period of time. If disabled, users of the administrator interface are never timed out. |
| `signalling_ports_end` | integer | The end value for the range of ports (UDP and TCP) that all Conferencing Nodes will use to send signaling (for H.323, H.245 and SIP). Range: 10000 to 49999. Default: 39999. |
| `signalling_ports_start` | integer | The start value for the range of ports (UDP and TCP) that all Conferencing Nodes will use to send signaling (for H.323, H.245 and SIP). Range: 10000 to 49999. Default: 33000. |
| `sip_tls_cert_verify_mode` | string | Determines whether to verify the peer certificate for connections over SIP TLS. Off: the peer certificate will be not be verified; all connections will be allowed. On: the peer certificate will be verified, and the peer's remote identities (according to RFC5922) will be compared against the Application Unique String (AUS) identified by the Pexip Infinity before the connection is allowed. |
| `site_banner` | string | Text of the banner to display on the top of every page of this Pexip Infinity administrator web interface. Maximum length: 255 characters. |
| `site_banner_bg` | string | The background color for the site banner. |
| `site_banner_fg` | string | The text color for the site banner. |
| `teams_enable_powerpoint_render` | boolean | Determines whether PowerPoint Live content is enabled for Microsoft Teams calls. |
| `waiting_for_chair_timeout` | integer | The length of time (in seconds) for which a Guest participant will remain at the waiting screen if a Host does not join, before being disconnected. Range: 0 to 86400. Default: 900. |
