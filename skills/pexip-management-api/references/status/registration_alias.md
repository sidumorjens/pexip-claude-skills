# Registration alias

**Endpoint:** `/api/admin/status/v1/registration_alias/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `alias` | string | The registered alias. Maximum length: 1000 characters. |
| `id` | integer | The primary key. |
| `is_natted` | boolean | Indicates whether the registration is behind a NAT. |
| `node` | string | The Conferencing Node used where the alias is registered. Maximum length: 50 characters. |
| `protocol` | string | The signaling protocol for the registration. |
| `push_token` | string | The Google Cloud Messaging push token for registration (may be blank). Maximum length: 1000 characters. |
| `registration_id` | string | The ID of the registered alias. |
| `remote_address` | string | The remote IP address used for signaling. Maximum length: 50 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `start_time` | datetime | Indicates the time the alias was registered. |
| `username` | string | The username used to authenticate the registration. Maximum length: 1000 characters. |
| `vendor` | string | The vendor information for the endpoint. Maximum length: 200 characters. |
