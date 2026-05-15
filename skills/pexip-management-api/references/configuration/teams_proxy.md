# Microsoft Teams Connector

**Endpoint:** `/api/admin/configuration/v1/teams_proxy/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `address` | string | The FQDN of the Teams Connector to use for outbound Teams calls. This is the FQDN (DNS name) of the Teams Connector load balancer in Azure that fronts the Teams Connector deployment. Maximum length: 255 characters. |
| `azure_tenant` | `azure_tenant` (related resource) | Azure tenant name |
| `description` | string | A description of the Teams Connector. Maximum length: 250 characters. |
| `eventhub_id` | string | The unique identifier of the queue. |
| `id` | integer | The primary key. |
| `min_number_of_instances` | integer | The minimum required number of instances in the scale set. This setting only applies when the Azure Event Hub is enabled, and is the number of instances that are always running when there are no scaling policies in effect (it overrides the manual scaling settings in the Azure portal). Default: 1. |
| `name` | string | The name used to refer to this Teams Connector. Teams Connectors can be assigned to system locations, call routing rules and Virtual Receptions. Maximum length: 250 characters. |
| `notifications_enabled` | boolean | When enabled, this provides the ability to create scheduled scaling policies, and also provides enhanced status information for each Teams Connector node, such as call capacity and current media load. |
| `notifications_queue` | string | The Connection string primary key for the Azure Event Hub (standard access policy). This is in the format Endpoint=sb://examplevmss-tzfk6222uo-ehn.servicebus.windows.net/;SharedAccessKeyName=standard_access_policy;SharedAccessKey=[string]/[string]/[string]=; |
| `port` | integer | The IP port of the Teams Connector. Range: 1 to 65535. Default: 443. |
| `resource_uri` | string | The URI that identifies this resource. |
| `updated` | datetime | The date and time teams connector configuration was updated. |
