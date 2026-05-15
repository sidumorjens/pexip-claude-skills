# external webapp host

**Endpoint:** `/api/admin/configuration/v1/external_webapp_host/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `address` | string | The FQDN or IP address of an external host used to serve a web app. Maximum length: 255 characters. |
| `id` | integer | The primary key. |
| `resource_uri` | string | The URI that identifies this resource. |
