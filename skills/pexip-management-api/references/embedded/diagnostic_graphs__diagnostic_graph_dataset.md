# Dataset

**Endpoint:** `/embedded/diagnostic_graphs/diagnostic_graph_dataset/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `color` | string | The color of the dataset |
| `graph` | `diagnostic_graphs` (related resource) | A single related resource. Can be either a URI or set of nested resource data. |
| `graph_type` | string | The Dataset graph type |
| `id` | integer | The primary key. |
| `metric_id` | string | The Dataset metric. |
| `metric_name` | string | The Dataset metric. |
| `multiplier` | float | The value to multiply every value from the dataset by before drawing it |
| `node` | string | The Node for the graph dataset. |
| `resource_uri` | string | The URI that identifies this resource. |
| `width` | integer | The width of the line used when displaying the dataset |
