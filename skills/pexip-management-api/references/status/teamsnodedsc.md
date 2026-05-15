# Teams Connector node DSC status

**Endpoint:** `/api/admin/status/v1/teamsnodedsc/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `details` | string | Teams Connector DSC details. |
| `failing_resources` | string | Teams Connector DSC failing resources. |
| `last_contact` | datetime | Teams Connector DSC last contacted. |
| `resource_uri` | string | The URI that identifies this resource. |
| `status` | string | Teams Connector DSC status. |
| `teamsnode_id` | `teamsnode` (related resource) | A single related resource. Can be either a URI or set of nested resource data. |
