# OTJ Exchange Autodiscover URL

**Endpoint:** `/api/admin/configuration/v1/mjx_exchange_autodiscover_url/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `description` | string | An optional description of this Exchange Autodiscover URL. Maximum length: 250 characters. |
| `exchange_deployment` | `mjx_exchange_deployment` (related resource) | The OTJ Exchange Integration this Autodiscover URL belongs to. |
| `id` | integer | The primary key. |
| `name` | string | The name of this Exchange Autodiscover URL. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `url` | string | The URL used to connect to the Autodiscover service on the Exchange deployment. Maximum length: 255 characters. |
