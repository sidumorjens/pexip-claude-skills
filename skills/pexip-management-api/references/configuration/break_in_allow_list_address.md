# Allow list address

**Endpoint:** `/api/admin/configuration/v1/break_in_allow_list_address/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `address` | string | The The IPv4 or IPv6 address for this allow list IP range. |
| `allowlist_entry_type` | string | The entry type of this address range.  Use 'User' for IP ranges containing trusted end-user workstations or hardware video endpoints;  use 'Proxy' for trusted reverse proxies. |
| `description` | string | A description of this break-in attempt IP allow list entry. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `ignore_incorrect_aliases` | boolean | Allow unlimited scan attempts (incorrect aliases dialled) that are received from addresses in this range. This should only be enabled in trusted environments. |
| `ignore_incorrect_pins` | boolean | Allow unlimited incorrect PIN attempts that are received from addresses in this range. This should only be enabled in trusted environments. |
| `name` | string | The name of this break-in attempt IP allow list entry. Maximum length: 250 characters. |
| `prefix` | integer | The prefix length used in conjunction with the Network address to determine the network addresses which this allow list contains. For example, use a Network address of 10.0.0.0 and a Network prefix of 8 to specify all addresses in the range 10.0.0.0 to 10.255.255.255. Range: 1 to 128. |
| `resource_uri` | string | The URI that identifies this resource. |
