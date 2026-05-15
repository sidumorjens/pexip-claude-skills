# Installable software bundle

**Endpoint:** `/api/admin/configuration/v1/software_bundle_revision/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `bundle_type` | string | Software bundle type. |
| `core` | boolean | Whether this software bundle instance is core. |
| `id` | integer | The primary key. |
| `resource_uri` | string | The URI that identifies this resource. |
| `revision` | string | Software bundle revision. |
| `version` | string | Software bundle version. |
