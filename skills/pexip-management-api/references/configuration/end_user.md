# User

**Endpoint:** `/api/admin/configuration/v1/end_user/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `avatar_url` | string | The avatar URL of the user. Maximum length: 255 characters. |
| `department` | string | The department of the user. Maximum length: 100 characters. |
| `description` | string | The description of the user. Maximum length: 250 characters. |
| `display_name` | string | The display name of the user. Maximum length: 250 characters. |
| `exchange_user_id` | string | The user's Exchange User ID. This is the unique identifier of the user on Exchange on-premises. |
| `first_name` | string | The first name of the user. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `last_name` | string | The last name of the user. Maximum length: 250 characters. |
| `mobile_number` | string | The mobile number of the user. Maximum length: 100 characters. |
| `ms_exchange_guid` | string | The user's Exchange Mailbox ID. Normally, this field is only populated when LDAP sync is enabled for customers with Exchange on-premises environments. |
| `primary_email_address` | string | The email address of the user. Maximum length: 100 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `sync_tag` | string | A unique identifier used to track which LDAP sync template created this user. Maximum length: 250 characters. |
| `telephone_number` | string | The telephone number of the user. Maximum length: 100 characters. |
| `title` | string | The title of the user. Maximum length: 128 characters. |
| `user_groups` | `user_group` (related resource) | The ID of the User Groups that this End User is a member of. |
| `user_oid` | string | The user's Microsoft 365 Object ID. This is the unique identifier of the user on Microsoft 365 services. |
| `uuid` | string | A unique identifier for this user which is used internally by Pexip. |
