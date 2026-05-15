# License

**Endpoint:** `/api/admin/configuration/v1/licence/`

## Allowed methods

- **Allowed Methods (list):** GET, POST
- **Allowed Methods (detail):** GET, DELETE

## Fields

| Field | Type | Description |
|---|---|---|
| `activatable` | integer | The available number of activatable licenses. |
| `activatable_overdraft` | integer | The available activatable license overdraft. |
| `concurrent` | integer | The available number of concurrent licenses. |
| `concurrent_overdraft` | integer | The available concurrent license overdraft. |
| `entitlement_id` | string | The license entitlement key used to activate this license. |
| `expiration_date` | string | The date and time at which this license expires. |
| `features` | string | The features this license provides. |
| `fulfillment_id` | string | The identifier for this license. |
| `fulfillment_type` | string | The type of this license. |
| `hybrid` | integer | The available number of hybrid licenses. |
| `hybrid_overdraft` | integer | The available hybrid license overdraft. |
| `license_type` | string | The type of feature this license provides. |
| `offline_mode` | boolean | Save this as a Stored license request for manual activation at a later date. |
| `product_id` | string | The type of this license. |
| `repair` | integer | The number of times this license has been repaired. |
| `resource_uri` | string | The URI that identifies this resource. |
| `server_chain` | string | The license server chain for this license. |
| `start_date` | string | The date and time at which this license becomes valid. |
| `status` | string | The status of this object. |
| `trust_flags` | integer | The trust status of this license. |
| `vendor_dictionary` | dict | The vendor-specific information associated with this license. |
