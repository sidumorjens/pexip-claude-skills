# OTJ Endpoint Group

**Endpoint:** `/api/admin/configuration/v1/mjx_endpoint_group/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `description` | string | An optional description of this OTJ Endpoint Group. Maximum length: 250 characters. |
| `disable_proxy` | boolean | Bypass the web proxy when sending requests to Cisco OBTP Endpoints in this OTJ Endpoint Group. |
| `endpoints` | `mjx_endpoint` (related resource) | The endpoints that belong to this Endpoint Group. |
| `id` | integer | The primary key. |
| `mjx_integration` | `mjx_integration` (related resource) | The One-Touch Join Profile to which this Endpoint Group belongs. |
| `name` | string | The name of this OTJ Endpoint Group. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `system_location` | `system_location` (related resource) | The system location of the Conferencing Nodes which will provide One-Touch Join services for this Endpoint Group. |
