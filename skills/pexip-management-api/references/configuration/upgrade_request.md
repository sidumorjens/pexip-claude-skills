# Upgrade request

**Endpoint:** `/api/admin/configuration/v1/upgrade_request/`

## Allowed methods

- **Allowed Methods:** DELETE, GET

## Fields

| Field | Type | Description |
|---|---|---|
| `current` | `version_info` (related resource) | A single related resource. Can be either a URI or set of nested resource data. |
| `offset` | integer | Integer data. Ex: 2673 |
| `resource_uri` | string | The URI that identifies this resource. |
| `state` | string | Status of snapshot request. |
| `upgrade` | `version_info` (related resource) | A single related resource. Can be either a URI or set of nested resource data. |
| `uuid` | string | Upgrade upload request ID. |
