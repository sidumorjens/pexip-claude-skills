# Exchange Metadata Domain or URL

**Endpoint:** `/api/admin/configuration/v1/exchange_domain/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `creation_time` | datetime | *Do not use this exchange_domain resource directly; changes should only be made by the Secure Scheduler for Exchange service.* The time at which this Exchange Metadata Domain or URL was created. |
| `domain` | string | An FQDN or URL which can be used to access a page containing the Exchange Metadata for your Exchange deployment, including the public key of the Microsoft Exchange Server Auth Certificate used by the add-in to verify user identities.  Maximum length: 192 characters. |
| `exchange_connector` | `ms_exchange_connector` (related resource) | A single related resource. Can be either a URI or set of nested resource data. |
| `id` | integer | The primary key. |
| `resource_uri` | string | The URI that identifies this resource. |
