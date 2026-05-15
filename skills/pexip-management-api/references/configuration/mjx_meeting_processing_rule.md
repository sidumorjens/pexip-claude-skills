# OTJ Meeting Processing Rule

**Endpoint:** `/api/admin/configuration/v1/mjx_meeting_processing_rule/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `company_id` | string | For a Meeting type of Teams SIP Guest Join or Google Meet SIP Guest Join: the Pexip Service Customer ID that OTJ will add to the dial string for CDRs to appear in Pexip Control Center. This field is required unless your SIP endpoints are registered to the Pexip cloud service. Maximum length: 36 characters. |
| `custom_template` | string | A Jinja2 template which is used to process the meeting information from calendar events in order to extract the meeting alias. Maximum length: 10240 characters. |
| `default_processing_enabled` | boolean | Apply default meeting processing rules for this meeting type. |
| `description` | string | The description of this Meeting Processing Rule. Maximum length: 250 characters. |
| `domain` | string | The domain associated with this meeting invitation. Maximum length: 255 characters. |
| `enabled` | boolean | Determines whether or not the rule is enabled. Any disabled rules still appear in the rules list but are ignored. Use this setting to test configuration changes, or to temporarily disable specific rules. |
| `id` | integer | The primary key. |
| `include_pin` | boolean | Append the meeting password to the alias, so that users do not have to enter the password themselves. |
| `match_string` | string | The regular expression that defines the string to search for in the invitation. Maximum length: 250 characters. |
| `meeting_type` | string | The meeting type of this Meeting Processing Rule. |
| `mjx_integration` | `mjx_integration` (related resource) | The One-Touch Join Profile associated with this Meeting Processing Rule. |
| `name` | string | The name of this Meeting Processing Rule. Maximum length: 250 characters. |
| `priority` | integer | The priority of this rule. Rules are checked in ascending priority order until the first matching rule is found, and it is then applied. Range: 1 to 200. |
| `replace_string` | string | A regular expression that defines how to transform the matched string into the alias to dial. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `transform_rule` | string | A Jinja2 template that is used to process the meeting information in order to extract the meeting alias. Maximum length: 512 characters. |
