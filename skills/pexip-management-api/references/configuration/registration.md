# Registration

**Endpoint:** `/api/admin/configuration/v1/registration/`

## Allowed methods

- **Allowed Methods (list):** GET
- **Allowed Methods (detail):** GET, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `adaptive_max_refresh` | integer | The maximum interval in seconds before a device's registration must be refreshed, when using the Adaptive strategy. Range: 60 to 7200. Default: 3600. |
| `adaptive_min_refresh` | integer | The minimum interval in seconds before a device's registration must be refreshed, when using the Adaptive strategy. Range: 60 to 3600. Default: 60. |
| `enable` | boolean | Allows devices to register to Pexip Infinity in order to receive calls. Devices must register with a permitted alias (Users & Devices > Device aliases). |
| `enable_google_cloud_messaging` | boolean | Enables sending of push notifications to registered mobile devices via the Google Cloud Messaging platform. |
| `enable_push_notifications` | boolean | Allows mobile devices to register to Pexip Infinity and receive push notifications. |
| `id` | integer | The primary key. |
| `maximum_max_refresh` | integer | The maximum interval in seconds before a device's registration must be refreshed, when using the Basic strategy. Range: 60 to 7200. Default: 300. |
| `maximum_min_refresh` | integer | The minimum interval in seconds before a device's registration must be refreshed, when using the Basic strategy. Range: 60 to 3600. Default: 60. |
| `natted_max_refresh` | integer | The maximum interval in seconds before a device's registration must be refreshed, for a SIP endpoint behind a NAT. Range: 60 to 3600. Default: 90. |
| `natted_min_refresh` | integer | The minimum interval in seconds before a device's registration must be refreshed, for a SIP endpoint behind a NAT. Range: 60 to 3600. Default: 60. |
| `push_token` | string | Customizes the Google Cloud Messaging push token. You should only change this setting if you are using a custom Pexip mobile application. |
| `refresh_strategy` | string | Defines which strategy to use when calculating the expiry time of a SIP or H.323 registration. Adaptive: Infinity automatically adjusts the refresh interval depending on the number of current registrations on the Conferencing Node handling the request, in order to spread the load of registration refreshes. Basic: Infinity simply uses the configured minimum and maximum settings, along with the requested value, to determine the refresh interval. |
| `resource_uri` | string | The URI that identifies this resource. |
| `route_via_registrar` | boolean | When enabled, all calls from registered legacy Infinity Connect clients are routed via the registrar, regardless of the domain being called. When disabled, calls are routed via normal DNS SRV lookups. |
