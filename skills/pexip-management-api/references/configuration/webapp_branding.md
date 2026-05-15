# Web app branding package

**Endpoint:** `/api/admin/configuration/v1/webapp_branding/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `branding_file` | file | Branding package to upload. |
| `description` | string | Description of this branding package. Maximum length: 250 characters. |
| `is_default` | boolean | Whether this is Pexip supplied default branding. |
| `last_updated` | datetime | The date and time when this branding package was last updated |
| `name` | string | The name given to this branding package |
| `resource_uri` | string | The URI that identifies this resource. |
| `uuid` | string | Branding package ID |
| `webapp_type` | string | The web app supported by this branding package |
