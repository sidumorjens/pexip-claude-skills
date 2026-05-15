# /api/admin/command/v1/platform/snapshot/

**Endpoint:** `/api/admin/command/v1/platform/snapshot/`

## Allowed methods

- **Allowed Methods (list):** POST

## Fields

| Field | Type | Description |
|---|---|---|
| `end_limit` | integer | The end time in hours for the diagnostic snapshot. |
| `include_diagnostic_metrics` | boolean | Include diagnostic metrics from all Conferencing Nodes |
| `limit` | integer | The start time in hours for the diagnostic snapshot. |
| `request` | boolean | Set to true to create a background diagnostic snapshot request instead |
