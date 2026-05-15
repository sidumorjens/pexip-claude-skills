# Diagnostic Graph

**Endpoint:** `/api/admin/configuration/v1/diagnostic_graphs/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `datasets` | `diagnostic_graph_dataset` (related resource) | The datasets for the diagnostic graph. |
| `id` | integer | The primary key. |
| `order` | integer | The order of the diagnostic graph. |
| `resource_uri` | string | The URI that identifies this resource. |
| `title` | string | The title of the diagnostic graph. |
