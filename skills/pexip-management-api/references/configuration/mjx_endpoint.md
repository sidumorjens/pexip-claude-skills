# OTJ Endpoint

**Endpoint:** `/api/admin/configuration/v1/mjx_endpoint/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `api_address` | string | The IP address or FQDN of the endpoint's API. Maximum length: 255 characters. |
| `api_password` | string | The password used by OTJ when accessing the endpoint's API; if left blank, the OTJ Profile default will be used. Maximum length: 100 characters. |
| `api_port` | integer | The port of the endpoint's API. Range: 1 to 65535. Default: 443 if HTTPS is used, otherwise 80 for HTTP. |
| `api_username` | string | The username used by OTJ when accessing the endpoint's API; if left blank, the OTJ Profile default will be used. Maximum length: 100 characters. |
| `description` | string | An optional description of this OTJ Endpoint. Maximum length: 250 characters. |
| `endpoint_type` | string | The type of OTJ feature supported by this endpoint. |
| `id` | integer | The primary key. |
| `mjx_endpoint_group` | `mjx_endpoint_group` (related resource) | The Endpoint Group to which this endpoint belongs. |
| `name` | string | The name of this OTJ Endpoint. Maximum length: 250 characters. |
| `poly_password` | string | The password the endpoint will use when connecting and authenticating to the calendaring service on the Conferencing Node. Maximum length: 100 characters. |
| `poly_raise_alarms_for_this_endpoint` | boolean | When enabled, an alarm will be raised if OTJ is unable to provide this endpoint with meeting information. |
| `poly_username` | string | The username the endpoint will use when connecting and authenticating to the calendaring service on the Conferencing Node. Maximum length: 150 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `room_resource_email` | string | The email address of the room resource corresponding to this endpoint. Maximum length: 150 characters. |
| `use_https` | string | Use HTTPS to access this endpoint's API. |
| `verify_cert` | string | Enable TLS verification when accessing the endpoint API. Only applicable if using HTTPS to access this endpoint's API. |
| `webex_device_id` | string | The Webex endpoint's unique identifier. |
