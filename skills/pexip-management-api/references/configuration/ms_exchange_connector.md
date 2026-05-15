# Secure Scheduler for Exchange Integration

**Endpoint:** `/api/admin/configuration/v1/ms_exchange_connector/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `accept_edited_occurrence_template` | string | *Do not use this ms_exchange_connector resource directly; changes should only be made by the Secure Scheduler for Exchange service.* A Jinja2 template that is used to produce the message sent to meeting organizers once the scheduling service successfully schedules an edited occurrence in a recurring series. Maximum length: 12288 characters. |
| `accept_edited_recurring_series_template` | string | A Jinja2 template that is used to produce the message sent to meeting organizers once the scheduling service successfully schedules an edited recurring meeting. Maximum length: 12288 characters. |
| `accept_edited_single_meeting_template` | string | A Jinja2 template that is used to produce the message sent to meeting organizers once the scheduling service successfully schedules an edited single meeting. Maximum length: 12288 characters. |
| `accept_new_recurring_series_template` | string | A Jinja2 template that is used to produce the message sent to meeting organizers once the scheduling service successfully schedules a new recurring meeting. Maximum length: 12288 characters. |
| `accept_new_single_meeting_template` | string | A Jinja2 template that is used to produce the message sent to meeting organizers once the scheduling service successfully schedules a new single meeting. Maximum length: 12288 characters. |
| `addin_application_id` | string | The Application (client) ID which was generated when creating the App Registration in Microsoft Entra for add-in authentication. |
| `addin_authentication_method` | string | The type of token the Outlook add-in uses to authenticate to Pexip |
| `addin_authority_url` | string | The Authority URL copied from the App Registration created in Microsoft Entra for add-in authentication. Maximum length: 255 characters. |
| `addin_button_label` | string | The label for the add-in button on desktop clients. Maximum length: 250 characters. |
| `addin_description` | string | The description of the add-in. Maximum length: 250 characters. |
| `addin_display_name` | string | The display name of the add-in. Maximum length: 250 characters. |
| `addin_group_label` | string | The name of the group in which to place the add-in button on desktop clients. Maximum length: 250 characters. |
| `addin_naa_web_api_application_id` | string | The Application (client) ID for the NAA Web API which was generated when creating the App Registration in Microsoft Entra. |
| `addin_oidc_metadata_url` | string | The OpenID Connect metadata document copied from the App Registration created in Microsoft Entra for add-in authentication. Maximum length: 255 characters. |
| `addin_pane_already_video_meeting_heading` | string | The heading that appears on the side pane when the add-in is activated after an alias has already been obtained for the meeting. Maximum length: 250 characters. |
| `addin_pane_already_video_meeting_message` | string | The message that appears on the side pane when the add-in is activated after an alias has already been obtained for the meeting. Maximum length: 250 characters. |
| `addin_pane_button_title` | string | The label of the button on the side pane used to add a single-use VMR. Maximum length: 250 characters. |
| `addin_pane_description` | string | The description of the add-in on the side pane. Maximum length: 250 characters. |
| `addin_pane_general_error_heading` | string | The heading that appears on the side pane when an error occurs trying to add the joining instructions. Maximum length: 250 characters. |
| `addin_pane_general_error_message` | string | The message that appears on the side pane when an error occurs trying to add the joining instructions of the single-use VMR. Maximum length: 250 characters. |
| `addin_pane_management_node_down_heading` | string | The heading that appears on the side pane when the Management Node cannot be contacted to obtain an alias. Maximum length: 250 characters. |
| `addin_pane_management_node_down_message` | string | The message that appears on the side pane when the Management Node cannot be contacted to obtain an alias. Maximum length: 250 characters. |
| `addin_pane_personal_vmr_add_button` | string | The label of the button on the side pane used to add a personal VMR. Maximum length: 250 characters. |
| `addin_pane_personal_vmr_error_getting_message` | string | The message that appears on the side pane when an error occurs trying to obtain a list of the user's personal VMRs. Maximum length: 250 characters. |
| `addin_pane_personal_vmr_error_inserting_meeting_message` | string | The message that appears on the side pane when an error occurs trying to add the personal VMR details to the meeting. Maximum length: 250 characters. |
| `addin_pane_personal_vmr_error_signing_in_message` | string | The message that appears on the side pane when an error occurs trying to sign the user in. Maximum length: 250 characters. |
| `addin_pane_personal_vmr_none_message` | string | The message that appears on the side pane when the user has no personal VMRs. Maximum length: 250 characters. |
| `addin_pane_personal_vmr_select_message` | string | The message that appears on the side pane requesting users to select a personal VMR to use for the meeting. Maximum length: 250 characters. |
| `addin_pane_personal_vmr_sign_in_button` | string | The label of the button on the side pane requesting users to sign in to obtain a list of their personal VMRs. Maximum length: 250 characters. |
| `addin_pane_success_heading` | string | The heading that appears on the side pane when when an alias has been obtained successfully from the Management Node. Maximum length: 250 characters. |
| `addin_pane_success_message` | string | he message that appears on the side pane when when an alias has been obtained successfully from the Management Node. Maximum length: 250 characters. |
| `addin_pane_title` | string | The title of the add-in on the side pane. Maximum length: 250 characters. |
| `addin_provider_name` | string | The name of the organization which provides the add-in. Maximum length: 250 characters. |
| `addin_server_domain` | string | The FQDN of the reverse proxy or Conferencing Node that provides the add-in content. The FQDN must have a valid certificate. Maximum length: 192 characters. |
| `addin_supertip_description` | string | The text of the supertip for the add-in button on desktop clients. Maximum length: 250 characters. |
| `addin_supertip_title` | string | The title of the supertip help text for the add-in button on desktop clients. Maximum length: 250 characters. |
| `additional_add_in_script_sources` | string | Optionally specify additional URLs to download JavaScript script files. Each URL must be entered on a separate line. Maximum length: 4096 characters. |
| `allow_new_users` | boolean | Disable this option to allow only those users with an existing User record to access the Outlook add-in. |
| `auth_provider` | string | The method by which users will sign into the Outlook add-in. |
| `authentication_method` | string | The method used to authenticate to Exchange |
| `conference_description_template` | string | A Jinja2 template that is used to produce the description of scheduled conferences. Maximum length: 12288 characters. |
| `conference_name_template` | string | A Jinja2 template that is used to produce the name of scheduled conferences. Please note conference names must be unique so a random number may be appended if the name that is generated is already in use by another service. Maximum length: 12288 characters. |
| `conference_subject_template` | string | A Jinja2 template that is used to produce the subject field of scheduled conferences. By default this will use the subject line of the meeting invitation but this field can be deleted or amended if you do not want the subject to be visible to administrators. Maximum length: 12288 characters. |
| `description` | string | An optional description of the Secure Scheduler for Exchange Integration. Maximum length: 250 characters. |
| `disable_proxy` | boolean | Disable the usage of any web proxy which may have been configured on the Management Node by this Secure Scheduler for Exchange Integration. |
| `domains` | `exchange_domain` (related resource) | The Exchange Metadata Domains / URLs associated with this Secure Scheduler for Exchange Integration. |
| `enable_addin_debug_logs` | boolean | Enable this option to view debug logs within the add-in side pane. Note that these logs will appear for all users of this add-in. |
| `enable_dynamic_vmrs` | boolean | Enable this option to allow Outlook users to schedule meetings in single-use (randomly generated) VMRs. |
| `enable_personal_vmrs` | boolean | Enable this option to allow Outlook users to schedule meetings in their personal VMRs. |
| `host_identity_provider_group` | `identity_provider_group` (related resource) | The set of Identity Providers to use if participants are required to authenticate in order to join the scheduled conference. If this is blank, participants will not be required to authenticate. |
| `id` | integer | The primary key. |
| `ivr_theme` | `ivr_theme` (related resource) | The theme for use with this service. |
| `kerberos_auth_every_request` | boolean | When Kerberos authentication is enabled, send a Kerberos Authorization header in every request to the Exchange server. |
| `kerberos_enable_tls` | boolean | If enabled, all communication to the KDC will go through an HTTPS proxy and all traffic to the KDC will be encrypted using TLS. |
| `kerberos_exchange_spn` | string | The Exchange Service Principal Name (SPN). Maximum length: 255 characters. |
| `kerberos_kdc` | string | The address of the Kerberos key distribution center (KDC). Maximum length: 255 characters. |
| `kerberos_kdc_https_proxy` | string | The URL of the Kerberos key distribution center (KDC) HTTPS proxy. Maximum length: 255 characters. |
| `kerberos_realm` | string | The Kerberos Realm, which is usually your domain in upper-case. Maximum length: 250 characters. |
| `kerberos_verify_tls_using_custom_ca` | boolean | If enabled, use the configured Root Trust CA Certificates to verify the KDC HTTPS proxy SSL certificate. If disabled, the HTTPS proxy SSL certificate is verified using the system-wide default set of trusted certificates. |
| `meeting_buffer_after` | integer | The number of minutes after the meeting's scheduled end of a conference participants will be able to join the VMR. Range: 0 to 180. Default: 60. |
| `meeting_buffer_before` | integer | The number of minutes before the meeting's scheduled start time that participants will be able to join the VMR. Range: 0 to 180. Default: 30. |
| `meeting_instructions_template` | string | A Jinja2 template that is used to generate the instructions added by the scheduling service to the body of the meeting request when a single-use VMR is being used. Maximum length: 12288 characters. |
| `microsoft_fabric_components_url` | string | The URL used to download the Microsoft Fabric Components CSS. Maximum length: 255 characters. |
| `microsoft_fabric_url` | string | The URL used to download the Microsoft Fabric CSS. Maximum length: 255 characters. |
| `name` | string | The name used to refer to the Secure Scheduler for Exchange Integration. Maximum length: 250 characters. |
| `non_idp_participants` | string | Determines whether participants attempting to join from devices other than Pexip apps (for example, SIP or H.323 endpoints) are permitted to join the conference when authentication is required. Disallow all: these devices may not join the conference directly, and will instead be placed in the waiting room. Allow if trusted: these devices may join the conference if they are locally registered, otherwise they will be placed in the waiting room. |
| `oauth_auth_endpoint` | string | The URI of the OAuth authorization endpoint. This should be copied from the 'Endpoints' section in Azure Active Directory App Registrations. Maximum length: 255 characters. |
| `oauth_client_id` | string | The Application ID which was generated when creating an App Registration in Azure Active Directory |
| `oauth_client_secret` | string | The OAuth Client Secret which was generated when creating an App Registration in Microsoft Entra |
| `oauth_redirect_uri` | string | The redirect URI you entered when creating an App Registration in Azure Active Directory. It should be in the format 'https://[Management Node Address]/admin/platform/msexchangeconnector/oauth_redirect/'. Maximum length: 255 characters. |
| `oauth_refresh_token` | string | The OAuth refresh token which is obtained after successfully signing in via the OAuth flow. Maximum length: 4096 characters. |
| `oauth_state` | string | A unique state which is used during the OAuth sign-in flow. |
| `oauth_token_endpoint` | string | The URI of the OAuth token endpoint. This should be copied from the 'Endpoints' section in Azure Active Directory App Registrations. Maximum length: 255 characters. |
| `office_js_url` | string | The URL used to download the Office.js JavaScript library. Maximum length: 255 characters. |
| `password` | string | The password of the service account to be used by the scheduling service. Maximum length: 100 characters. |
| `personal_vmr_adfs_relying_party_trust_identifier` | string | The URL which identifies the OAuth 2.0 resource on AD FS. Maximum length: 255 characters. |
| `personal_vmr_description_template` | string | A Jinja2 template that is used to generate the description of the personal VMR, shown to users when they hover over the button. Maximum length: 12288 characters. |
| `personal_vmr_instructions_template` | string | A Jinja2 template that is used to produce the joining instructions added by the scheduling service to the body of the meeting request when a personal VMR is being used. Maximum length: 12288 characters. |
| `personal_vmr_location_template` | string | A Jinja2 template that is used to generate the text that will be inserted into the Location field of the meeting request when a personal VMR is being used. Maximum length: 12288 characters. |
| `personal_vmr_name_template` | string | A Jinja2 template that is used to generate the name of the personal VMR, as it appears on the button offered to users. Maximum length: 12288 characters. |
| `personal_vmr_oauth_auth_endpoint` | string | The authorization URI of the OAuth application used to authenticate users when signing in to the Outlook add-in. Maximum length: 255 characters. |
| `personal_vmr_oauth_client_id` | string | The client ID of the OAuth application used to authenticate users when signing in to the Outlook add-in. |
| `personal_vmr_oauth_client_secret` | string | The client secret of the OAuth application created for signing in users in the Outlook add-in. |
| `personal_vmr_oauth_token_endpoint` | string | The token URI of the OAuth application used to authenticate users when signing in to the Outlook add-in. Maximum length: 255 characters. |
| `placeholder_instructions_template` | string | The text that is added by the scheduling service to email messages when the actual joining instructions cannot be obtained. Maximum length: 12288 characters. |
| `private_key` | string | The private key used by this Secure Scheduler for Exchange Integration. Maximum length: 12288 characters. |
| `public_key` | string | The public key used by this Secure Scheduler for Exchange Integration. Maximum length: 12288 characters. |
| `reject_alias_conflict_template` | string | A Jinja2 template that is used to produce the message sent to meeting organizers when the scheduling service fails to schedule a meeting because the alias conflicts with an existing alias. Maximum length: 12288 characters. |
| `reject_alias_deleted_template` | string | The text that is sent to meeting organizers when the scheduling service fails to schedule a meeting because the alias for this meeting has been deleted. Maximum length: 12288 characters. |
| `reject_general_error_template` | string | A Jinja2 template that is used to produce the message sent to meeting organizers when the scheduling service fails to schedule a meeting because a general error occurred. Maximum length: 12288 characters. |
| `reject_invalid_alias_id_template` | string | The text that is sent to meeting organizers when the scheduling service fails to schedule a meeting because the alias ID in the meeting email is invalid. Maximum length: 12288 characters. |
| `reject_recurring_series_past_template` | string | The text that is sent to meeting organizers when the scheduling service fails to schedule a recurring meeting because all occurrences occur in the past. Maximum length: 12288 characters. |
| `reject_single_meeting_past` | string | The text that is sent to meeting organizers when the scheduling service fails to schedule a meeting because it occurs in the past. Maximum length: 12288 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `room_mailbox_email_address` | string | The email address of the equipment resource or room resource that is to be used by the scheduling service. Maximum length: 100 characters. |
| `room_mailbox_name` | string | The name of the equipment resource or room resource that is to be used by the scheduling service. Maximum length: 250 characters. |
| `scheduled_alias_description_template` | string | A Jinja2 template that is used to produce the description of scheduled conference aliases. Maximum length: 12288 characters. |
| `scheduled_alias_domain` | string | The domain to use when generating aliases for scheduled conferences. Maximum length: 192 characters. |
| `scheduled_alias_prefix` | string | The prefix to use when generating aliases for scheduled conferences. Minimum length: 1 characters. Maximum length: 8 characters. |
| `scheduled_alias_suffix_length` | integer | The length of the random number suffix part of aliases used for scheduled conferences. Range: 5 to 15. |
| `url` | string | The URL used to connect to Exchange Web Services (EWS) on the Exchange server. Maximum length: 255 characters. |
| `use_custom_add_in_sources` | boolean | Enable this to specify custom locations to serve add-in JavaScript and CSS from. This can be used to support offline deployments. |
| `username` | string | The username of the service account to be used by the scheduling service. Maximum length: 100 characters. |
| `uuid` | string | The unique identifier of the Secure Scheduler for Exchange Integration. |
