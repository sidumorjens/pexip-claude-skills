# Software bundle revision

**Endpoint:** `/api/admin/configuration/v1/software_bundle/`

## Allowed methods

- **Allowed Methods (list):** GET
- **Allowed Methods (detail):** PATCH, GET

## Fields

| Field | Type | Description |
|---|---|---|
| `bundle_type` | string | Selected software bundle type. |
| `id` | integer | The primary key. |
| `resource_uri` | string | The URI that identifies this resource. |
| `selected_revision` | `software_bundle_revision` (related resource) | Selected software bundle. |
