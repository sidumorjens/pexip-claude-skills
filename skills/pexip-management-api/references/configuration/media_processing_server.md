# Media processing server

**Endpoint:** `/api/admin/configuration/v1/media_processing_server/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `app_id` | string | The Application ID used when connecting to the AIMS server. |
| `fqdn` | string | The FQDN of the AIMS server used to process media.  Maximum length: 255 characters. |
| `id` | integer | The primary key. |
| `public_jwt_key` | string | JWT public key. |
| `resource_uri` | string | The URI that identifies this resource. |
