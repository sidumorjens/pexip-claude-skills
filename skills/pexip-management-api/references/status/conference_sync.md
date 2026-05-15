# Status

**Endpoint:** `/api/admin/status/v1/conference_sync/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `configuration_id` | integer | The primary key of the LDAP sync status. |
| `devices_created` | integer | The number of devices created in the LDAP sync operation. |
| `devices_deleted` | integer | The number of devices deleted in the LDAP sync operation. |
| `devices_unchanged` | integer | The number of devices unchanged in the LDAP sync operation. |
| `devices_updated` | integer | The number of devices updated in the LDAP sync operation. |
| `end_users_created` | integer | The number of users created in the LDAP sync operation. |
| `end_users_deleted` | integer | The number of users deleted in the LDAP sync operation. |
| `end_users_unchanged` | integer | The number of users unchanged in the LDAP sync operation. |
| `end_users_updated` | integer | The number of users updated in the LDAP sync operation. |
| `id` | integer | The primary key. |
| `last_updated` | datetime | The time at which the LDAP sync status was last updated. |
| `resource_uri` | string | The URI that identifies this resource. |
| `sync_errors` | integer | The number of errors in the LDAP sync operation. |
| `sync_last_error_description` | string | Description of the last LDAP synchronization error. |
| `sync_progress` | integer | Progress of the LDAP sync operation. |
| `sync_status` | string | Status of ongoing and completed LDAP synchronization attempts. |
| `vmrs_created` | integer | The number of VMRs created in the LDAP sync operation. |
| `vmrs_deleted` | integer | The number of VMRs deleted in the LDAP sync operation. |
| `vmrs_unchanged` | integer | The number of VMRs unchanged in the LDAP sync operation. |
| `vmrs_updated` | integer | The number of VMRs updated in the LDAP sync operation. |
