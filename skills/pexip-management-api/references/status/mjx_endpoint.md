# OTJ Endpoint

**Endpoint:** `/api/admin/status/v1/mjx_endpoint/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `endpoint_address` | string | The IP address or FQDN of the endpoint. |
| `endpoint_name` | string | The name of this OTJ endpoint. |
| `endpoint_type` | string | The type of OTJ feature supported by this endpoint. |
| `id` | integer | The primary key. |
| `last_contact_time` | datetime | The most recent time at which there was contact with this endpoint for OTJ meeting information. |
| `last_worker` | string | The Conferencing Node that most recently received a request or sent a request for OTJ meeting information. |
| `mjx_integration_name` | string | The name of the One-Touch Join Profile associated with this OTJ Meeting. Maximum length: 250 characters. |
| `number_of_meetings` | integer | The number of meetings last synced to the endpoint. |
| `resource_uri` | string | The URI that identifies this resource. |
| `room_email` | string | The email of the meeting room used for this One-Touch Join Meeting. Maximum length: 150 characters. |
