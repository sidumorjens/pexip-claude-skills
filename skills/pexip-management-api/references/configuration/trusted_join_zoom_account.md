# Trusted Zoom Account

**Endpoint:** `/api/admin/configuration/v1/trusted_join_zoom_account/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `customer_id` | string | Zoom account number as shown on the Zoom profile page. |
| `description` | string | An optional description of the Zoom account. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `resource_uri` | string | The URI that identifies this resource. |
