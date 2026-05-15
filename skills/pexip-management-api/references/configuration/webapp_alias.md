# Web app path

**Endpoint:** `/api/admin/configuration/v1/webapp_alias/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `branding` | `webapp_branding` (related resource) | Which branding package to use with this path. Select null to use the default. |
| `bundle` | `software_bundle_revision` (related resource) | Which web app bundle to use with this path. Select null to use the default. |
| `description` | string | Description of this web app path. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `is_default` | boolean | Select this option if you want /webapp to redirect to this particular path and associated branding. |
| `is_enabled` | boolean | Is this path enabled? |
| `resource_uri` | string | The URI that identifies this resource. |
| `slug` | string | Unique path component. |
| `webapp_type` | string | The selection of which web app to use with this path |
