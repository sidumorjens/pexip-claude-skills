# Registration alias

**Endpoint:** `/api/admin/history/v1/registration_alias/`

## Allowed methods

- **Allowed Methods (list):** GET
- **Allowed Methods (detail):** GET, DELETE

## Fields

| Field | Type | Description |
|---|---|---|
| `alias` | string | The registered alias. Maximum length: 1000 characters. |
| `end_time` | datetime | Indicates the time the alias was deregistered. |
| `id` | integer | The primary key. |
| `is_natted` | boolean | Indicates whether the registration was behind a NAT. |
| `node` | string | The Conferencing Node used where the alias was registered. Maximum length: 50 characters. |
| `protocol` | string | The signaling protocol for the registration. |
| `registration_id` | string | The ID of the registered alias. |
| `remote_address` | string | The remote IP address used for signaling. Maximum length: 50 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `start_time` | datetime | Indicates the time the alias was registered. |
| `username` | string | The username used to authenticate the registration. Maximum length: 1000 characters. |
| `vendor` | string | The vendor information for the endpoint. Maximum length: 200 characters. |
