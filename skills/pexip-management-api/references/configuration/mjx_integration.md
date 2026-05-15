# OTJ Profile

**Endpoint:** `/api/admin/configuration/v1/mjx_integration/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `description` | string | An optional description of this One-Touch Join Profile. Maximum length: 250 characters. |
| `display_upcoming_meetings` | integer | The number of days of upcoming One-Touch Join meetings to be shown on endpoints. Range: 0 to 365. Default: 7. |
| `enable_non_video_meetings` | boolean | When enabled, if the invitation has no valid video address the meeting will still appear on the endpoint as a scheduled meeting, but the Join button will not appear. |
| `enable_private_meetings` | boolean | Determines whether or not meetings flagged as private are processed by the OTJ service. |
| `end_buffer` | integer | The number of minutes after the meeting's scheduled end time that the Join button on the endpoint will remain enabled. Range: 0 to 180. Default: 0. |
| `endpoint_groups` | `mjx_endpoint_group` (related resource) | The Endpoint Groups used by this One-Touch Join Profile. |
| `ep_password` | string | The password used by OTJ to access a Cisco OBTP endpoint's API; only used if the endpoint's password is left blank. Maximum length: 100 characters. |
| `ep_use_https` | boolean | Whether or not to use HTTPS by default when accessing a Cisco OBTP endpoint's API. Can be overridden per endpoint. |
| `ep_username` | string | The username used by OTJ to access a Cisco OBTP endpoint's API; only used if the endpoint's username is left blank. Maximum length: 100 characters. |
| `ep_verify_certificate` | boolean | Whether or not to verify the TLS certificate of a Cisco OBTP endpoint by default when accessing its API. Can be overridden per endpoint. |
| `exchange_deployment` | `mjx_exchange_deployment` (related resource) | The OTJ Exchange Integration associated with this One-Touch Join Profile. |
| `google_deployment` | `mjx_google_deployment` (related resource) | The OTJ Google Workspace Integration associated with this One-Touch Join Profile. |
| `graph_deployment` | `mjx_graph_deployment` (related resource) | The OTJ O365 Graph Integration associated with this One-Touch Join Profile. |
| `id` | integer | The primary key. |
| `name` | string | The name of this One-Touch Join Profile. Maximum length: 250 characters. |
| `process_alias_private_meetings` | boolean | When enabled, the meeting alias for private meetings will be extracted from the invitation in the usual way. When disabled, the meeting alias will not appear on the endpoint and therefore the Join button will be disabled. |
| `replace_empty_subject` | boolean | For meetings that do not have a subject, use the organizer's name in place of the subject. |
| `replace_subject_template` | string | A Jinja2 snippet that defines how the subject should be replaced (when this has been enabled).If this field is left blank, the subject will be replaced with the name of the organizer.Maximum length: 512 characters. |
| `replace_subject_type` | string | Whether the meeting subject should be replaced. When enabled, the subject will be replaced with the name of the organizer unless you specify an alternative in the Replace subject string field. |
| `resource_uri` | string | The URI that identifies this resource. |
| `start_buffer` | integer | The number of minutes before the meeting's scheduled start time that the Join button on the endpoint will become enabled. Range: 0 to 180. Default: 5. |
| `use_webex` | boolean | Enable OTJ to connect to Webex endpoints via Webex Cloud |
| `webex_api_domain` | string | The FQDN to use when connecting to the Webex API. Maximum length: 192 characters. |
| `webex_client_id` | string | The Client ID that was generated when creating a Webex Integration for OTJ. Maximum length: 100 characters. |
| `webex_client_secret` | string | The Client Secret that was generated when creating a Webex Integration for OTJ. |
| `webex_oauth_state` | string | The OAuth State parameter used to verify Oauthendpoint's API. Can be overridden per endpoint. |
| `webex_redirect_uri` | string | The redirect URI you entered when creating a Webex Integration for OTJ. It must be in the format 'https://[Management Node Address]/admin/platform/mjxintegration/oauth_redirect/'. Maximum length: 255 characters. |
| `webex_refresh_token` | string | The Webex Refresh token for your webex integration Maximum length: 4096 characters. |
