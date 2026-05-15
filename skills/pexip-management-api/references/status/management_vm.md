# Management Node

**Endpoint:** `/api/admin/status/v1/management_vm/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `configuration_id` | integer | The primary key of the Management Node configuration. |
| `id` | integer | The primary key. |
| `last_attempted_contact` | datetime | The last time at which an attempt to contact the Management Node was made. |
| `last_updated` | datetime | The time at which the Management Node was last updated. |
| `name` | string | The hostname for this Management Node. Maximum length: 32 characters. |
| `primary` | boolean | Boolean data. Ex: True |
| `resource_uri` | string | The URI that identifies this resource. |
| `sync_status` | string | This node's configuration synchronisation state. |
| `upgrade_status` | string | The current upgrade status of the Management Node. |
| `version` | string | The software version of this Management Node. |
