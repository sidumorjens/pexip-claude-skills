# LDAP sync template

**Endpoint:** `/api/admin/configuration/v1/conference_sync_template/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `alias_1` | string | The pattern to use to generate the alias (string) that participants can dial to join this VMR. You should structure this pattern to generate a unique alias for the VMR. For example: meet.{{givenName\|lower}}.{{sn\|lower}}@example.com. Maximum length: 512 characters. |
| `alias_1_description` | string | The pattern to use to generate a description of the alias (optional). Maximum length: 512 characters. |
| `alias_2` | string | The pattern for an alternative string that participants can dial to join the VMR. For example: meet.{{givenName\|lower}}.{{sn\|lower}}. Maximum length: 512 characters. |
| `alias_2_description` | string | The pattern to use to generate a description of the alias (optional). Maximum length: 512 characters. |
| `alias_3` | string | The pattern for an alternative string that participants can dial to join the VMR. For example: {{ telephoneNumber\|pex_tail(6) }}. Maximum length: 512 characters. |
| `alias_3_description` | string | The pattern to use to generate a description of the alias (optional). Maximum length: 512 characters. |
| `alias_4` | string | The pattern for an alternative string that participants can dial to join the VMR. Maximum length: 512 characters. |
| `alias_4_description` | string | The pattern to use to generate a description of the alias (optional). Maximum length: 512 characters. |
| `alias_5` | string | The pattern for an alternative string that participants can dial to join the VMR. Maximum length: 512 characters. |
| `alias_5_description` | string | The pattern to use to generate a description of the alias (optional). Maximum length: 512 characters. |
| `alias_6` | string | The pattern for an alternative string that participants can dial to join the VMR. Maximum length: 512 characters. |
| `alias_6_description` | string | The pattern to use to generate a description of the alias (optional). Maximum length: 512 characters. |
| `alias_7` | string | The pattern for an alternative string that participants can dial to join the VMR. Maximum length: 512 characters. |
| `alias_7_description` | string | The pattern to use to generate a description of the alias (optional). Maximum length: 512 characters. |
| `alias_8` | string | The pattern for an alternative string that participants can dial to join the VMR. Maximum length: 512 characters. |
| `alias_8_description` | string | The pattern to use to generate a description of the alias (optional). Maximum length: 512 characters. |
| `aliases_overridable` | boolean | Allows aliases and alias descriptions for a VMR to be added, removed or modified in any way. When enabled this means that after the initial creation of a VMR and its aliases, subsequent syncs will not change any of the aliases or their descriptions (including any which were created by VMR alias 1..8 pattern and Description 1..8 pattern even if those patterns are modified in this template). |
| `allow_guests` | boolean | Yes: the conference will have two types of participants: Hosts and Guests. You must configure a Host PIN in the field above to be used by the Hosts. You can optionally configure a Guest PIN in the field below; if you do not enter a Guest PIN, Guests can join without a PIN, but the meeting will not start until the first Host has joined. No: all participants will have Host privileges. |
| `call_type` | string | Maximum media content of the conference. Participants will not be able to escalate beyond the selected capability. |
| `call_type_overridable` | boolean | Allows the conference capabilities setting to be manually overridden for each VMR. |
| `callrates_overridable` | boolean | Allows the auto-generated maximum inbound call bandwidth and outbound call bandwidth to be manually overridden for each VMR. |
| `conference_description` | string | The pattern to use to generate the VMR description. Maximum length: 250 characters. |
| `conference_description_overridable` | boolean | Allows the auto-generated VMR description to be manually overridden for each VMR. |
| `conference_name` | string | The pattern to use to generate the name of the VMR. You should structure this pattern to generate a unique VMR name. For example: {{givenName}} {{sn}} VMR. Maximum length: 250 characters. |
| `crypto_mode` | string | Controls the media encryption requirements for participants connecting to this service. Use global setting: Use the global media encryption setting (Platform > Global Settings). Required: All participants  (including RTMP participants) must use media encryption. Best effort: Each participant will use media encryption if their device supports it, otherwise the connection will be unencrypted. No encryption: All H.323, SIP and MS-SIP participants must use unencrypted media. (RTMP participants will use encryption if their device supports it, otherwise the connection will be unencrypted.) |
| `crypto_mode_overridable` | boolean | Allows the media encryption setting to be manually overridden for each VMR. |
| `description` | string | An optional description of this sync template. Maximum length: 250 characters. |
| `device_alias` | string | The pattern for the alias that will be registered by the device and be used by people trying to call the device. VMR. For example: {{mail}}. Maximum length: 512 characters. |
| `device_description` | string | The pattern to use when generating the optional description of this device. Maximum length: 512 characters. |
| `device_description_overridable` | boolean | Allows the auto-generated device description to be manually overridden for each device. |
| `device_email_subject_template` | string | A template for the subject of the email to be sent when a device is created or updated. Maximum length: 255 characters. |
| `device_email_template` | string | A template for the email to be sent when a device is created or updated. Maximum length: 24576 characters. |
| `device_enable_h323` | boolean | Allows the device to register using the H323 protocol. |
| `device_enable_infinity_connect_non_sso` | boolean | Allows legacy Infinity Connect clients to register using a username and password. |
| `device_enable_infinity_connect_sso` | boolean | Allows legacy Infinity Connect clients to register using AD FS Single Sign-On (SSO) services. |
| `device_enable_sip` | boolean | Allows the device to register using the SIP protocol. |
| `device_enable_standard_sso` | boolean | Allows a device to register and authenticate the registration against a SAML or OIDC Identity Provider. In order for this option to take effect, registrations must be enabled globally. |
| `device_password` | string | The pattern to user when generating the password for this device. Maximum length: 250 characters. |
| `device_password_overridable` | boolean | Allows the password to be manually overridden for each device. |
| `device_registration_types_overridable` | boolean | Allows the auto-generated device registration settings to be manually overridden for each device. |
| `device_sso_identity_provider_group` | `identity_provider_group` (related resource) | Select the set of Identity Providers which may be used to authenticate with when IdP SSO is enabled. |
| `device_sync_if_account_disabled` | boolean | Syncs all device aliases, even if the corresponding LDAP account is disabled. By default, device aliases are only provisioned if the corresponding LDAP account is enabled in the LDAP directory. If selected, a device alias will be created for LDAP accounts that are marked as disabled. This may be useful, for example, if you have a disabled machine account in LDAP corresponding to a SIP or H.323 room system - however it is not generally useful for staff accounts because if an employee leaves an organization you usually want their device record to be deleted automatically after their account is disabled in the corporate LDAP directory. |
| `device_tag` | string | The pattern for the unique identifier used to track usage of the device. Maximum length: 250 characters. |
| `device_tag_overridable` | boolean | Allows the auto-generated device tag to be manually overridden for each device. |
| `device_username` | string | The pattern to use to generate the username of this device. Maximum length: 100 characters. |
| `device_username_overridable` | boolean | Allows the username to be manually overridden for each device. |
| `direct_media` | string | Allows this VMR to use direct media between participants. When enabled, the VMR provides non-transcoded, encrypted, point-to-point calls between any two WebRTC participants. |
| `direct_media_notification_duration` | integer | The number of seconds to show a notification before being escalated into a transcoded call, or de-escalated into a direct media call. Range: 0s to 30s. Default: 0s. |
| `direct_media_notification_duration_overridable` | boolean | Allows the direct media notification duration to be manually overridden for each VMR. |
| `direct_media_overridable` | boolean | Allows the direct media settings to be manually overridden for each VMR. |
| `enable_active_speaker_indication` | boolean | Speaker display name or alias will be shown across the bottom of their video image. |
| `enable_automatic_sync` | boolean | Enables automatic (once per day) syncing of this template. As template synchronization can result in the automatic creation, modification or deletion of large numbers of VMRs, devices and users, we recommend that you only enable automatic syncing after you have manually synced at least once and have verified that you are satisfied with your sync template configuration. |
| `enable_chat` | string | Enables relay of chat messages between conference participants using supported clients such as the Pexip apps. You can use this option to override the global configuration setting. |
| `enable_chat_overridable` | boolean | Allows the enable chat setting to be manually overridden for each VMR. |
| `enable_overlay_text` | boolean | If enabled, the display name or alias will be shown for each participant. |
| `enable_service_emails` | boolean | Sends an email to the VMR or device owner whenever a synchronization creates a new VMR or device, or modifies an existing VMR or device. |
| `end_user_advanced_overridable` | boolean | Allows the auto-generated user advanced options to be manually overridden for each user. |
| `end_user_avatar_url` | string | The pattern to use to generate the avatar URL of the user. Maximum length: 512 characters. |
| `end_user_contacts_overridable` | boolean | Allows the auto-generated user contact information to be manually overridden for each user. |
| `end_user_department` | string | The pattern to use to generate the department of the user. Maximum length: 512 characters. |
| `end_user_description` | string | The pattern to use when generating the optional description of this user. Maximum length: 512 characters. |
| `end_user_description_overridable` | boolean | Allows the auto-generated user description to be manually overridden for each user. |
| `end_user_display_name` | string | The pattern to use to generate the display name of the user. Maximum length: 512 characters. |
| `end_user_first_name` | string | The pattern to use to generate the first name of the user. Maximum length: 512 characters. |
| `end_user_last_name` | string | The pattern to use to generate the last name of the user. Maximum length: 512 characters. |
| `end_user_mobile_number` | string | The pattern to use to generate the mobile number of the user. Maximum length: 512 characters. |
| `end_user_ms_exchange_guid` | string | The pattern to use to generate the Exchange Mailbox UUID of the user. This field is not required but if included must be in a UUID format and be unique for each user. Maximum length: 512 characters. |
| `end_user_names_overridable` | boolean | Allows the auto-generated user names to be manually overridden for each user. |
| `end_user_other_personal_overridable` | boolean | Allows the auto-generated user personal information to be manually overridden for each user. |
| `end_user_telephone_number` | string | The pattern to use to generate the telephone number of the user. Maximum length: 512 characters. |
| `end_user_title` | string | The pattern to use to generate the title of the user. Maximum length: 512 characters. |
| `end_user_uuid` | string | The pattern to use to generate the UUID of the user. This field is required and must be unique for each user and must be in a UUID format. Therefore it is strongly recommended to use {{objectGUID\|pex_to_uuid}} as the value of this pattern. Maximum length: 512 characters. |
| `guest_identity_provider_group` | `identity_provider_group` (related resource) | Select the set of Identity Providers to be offered to Guests to authenticate with, in order to join the conference. If this is blank, Guests will not be required to authenticate. |
| `guest_pin` | string | The pattern to use to generate the Guest PIN (if required). Length: 4-512 digits. |
| `guests_can_present` | boolean | If enabled, Guests can present into the conference. |
| `guests_can_present_overridable` | boolean | Allows the Guests can present setting to be manually overridden for each VMR. |
| `host_identity_provider_group` | `identity_provider_group` (related resource) | Select the set of Identity Providers to be offered to Hosts to authenticate with, in order to join the conference. If this is blank, Hosts will not be required to authenticate. |
| `host_view` | string | The layout that Hosts will see. |
| `host_view_overridable` | boolean | Allows the type of layout and whether to show names of participants to be manually overridden for each VMR. |
| `id` | integer | The primary key. |
| `idp_settings_overridable` | boolean | Allows the Host and Guest IdP Group settings to be manually overridden for each VMR. |
| `ivr_theme` | `ivr_theme` (related resource) | The theme to use with this service. If no theme is selected here, files from the global default theme (Platform > Global settings > Default theme) are used. |
| `ivr_theme_overridable` | boolean | Allows the theme to be manually overridden for each VMR. |
| `ldap_sync_source` | `ldap_sync_source` (related resource) | The LDAP data source to use when syncing records. |
| `ldap_user_filter` | string | The LDAP filter used to match user records in the directory. Default: (&(objectclass=person)(!(objectclass=computer))). Maximum length: 1024 characters. |
| `ldap_user_search_dn` | string | The DN relative to the base DN to query for user records (e.g. ou=people). If blank, the base DN from the LDAP sync source is used. Maximum length: 255 characters. |
| `max_callrate_in` | integer | This optional field allows you to limit the bandwidth of media being received by Pexip Infinity from each individual participant dialed in to this Virtual Meeting Room. Range: 128 to 8192. |
| `max_callrate_out` | integer | This optional field allows you to limit the bandwidth of media being sent by Pexip Infinity to each individual participant dialed in to this Virtual Meeting Room. Range: 128 to 8192. Default: 4128. |
| `max_pixels_per_second` | string | Sets the maximum call quality for each participant. |
| `max_pixels_per_second_overridable` | boolean | Allows the maximum call quality setting to be manually overridden for each VMR. |
| `name` | string | The name of this sync template. Maximum length: 250 characters. |
| `non_idp_participants` | string | Determines whether participants attempting to join from devices other than Pexip apps (for example, SIP or H.323 endpoints) are permitted to join the conference when authentication is required. Disallow all: these devices may not join the conference directly, and will instead be placed in the waiting room. Allow if trusted: these devices may join the conference if they are locally registered, otherwise they will be placed in the waiting room. |
| `non_idp_participants_overridable` | boolean | Allows the Other Participants setting to be manually overridden for each VMR. |
| `participant_limit` | integer | This optional field allows you to limit the number of participants allowed to join this Virtual Meeting Room. Range: 0 to 1000000. |
| `participant_limit_overridable` | boolean | Allows the auto-generated participant limit to be manually overridden for each VMR. |
| `pin` | string | The pattern to use to generate the Host PIN (if required). Length: 4-512 digits. |
| `pin_settings_overridable` | boolean | Allows the auto-generated Host and Guest PIN settings to be manually overridden for each VMR. |
| `primary_owner_email_address` | string | The email address of the owner of this VMR. The generated email will be sent to this address. For example: {{mail}}. Maximum length: 100 characters. |
| `primary_owner_email_address_overridable` | boolean | Allows the auto-generated email address to be manually overridden for each VMR. |
| `resource_uri` | string | The URI that identifies this resource. |
| `service_email_subject_template` | string | A template for the subject of the email to be sent when a VMR is created or updated. Maximum length: 255 characters. |
| `service_email_template` | string | A template for the email to be sent when a VMR is created or updated. Maximum length: 24576 characters. |
| `service_type` | string | The type of conferencing service. conference: A Virtual Meeting Room. lecture: A Virtual Auditorium. two_stage_dialing: A Virtual Reception. |
| `smtp_server` | `smtp_server` (related resource) | Email server to use for sending notification emails |
| `sync_conferences` | boolean | Enables VMR synchronization for this template. |
| `sync_devices` | boolean | Enables device alias synchronization for this template. |
| `sync_end_users` | boolean | Enables user synchronization for this template. |
| `tag` | string | The pattern for the unique identifier used to track usage of the service. Maximum length: 250 characters. |
| `tag_overridable` | boolean | Allows the auto-generated service tag to be manually overridden for each VMR. |
