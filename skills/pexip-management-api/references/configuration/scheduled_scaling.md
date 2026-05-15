# scheduled scaling policy

**Endpoint:** `/api/admin/configuration/v1/scheduled_scaling/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `enabled` | boolean | Determines whether or not this scheduled scaling policy is enabled. |
| `fri` | boolean | Indicates whether or not the policy should be applied on Friday. |
| `id` | integer | The primary key. |
| `instances_to_add` | integer | The number of instances to add when this policy is in effect. |
| `local_timezone` | string | The timezone used to specify the activation date and time. |
| `minutes_in_advance` | integer | The number of minutes in advance of the activation time to begin scaling up the instances. It can take up to 20 minutes to start an instance so this is to allow enough time for all of the requested additional instances to be started up. |
| `mon` | boolean | Indicates whether or not the policy should be applied on Monday. |
| `policy_name` | string | The name / description of this scheduled scaling policy. |
| `policy_type` | string | Policy type. |
| `resource_identifier` | string | The Teams Connector associated with this scheduling policy. |
| `resource_uri` | string | The URI that identifies this resource. |
| `sat` | boolean | Indicates whether or not the policy should be applied on Saturday. |
| `start_date` | date | The date from which this policy applies. String in format YYYY-MM-DD. |
| `sun` | boolean | Indicates whether or not the policy should be applied on Sunday. |
| `thu` | boolean | Indicates whether or not the policy should be applied on Thursday. |
| `time_from` | time | The time of day when the additional instances are required. String in format HH:MM:SS. |
| `time_to` | time | The time of day when the additional instances should be stopped. String in format HH:MM:SS. |
| `tue` | boolean | Indicates whether or not the policy should be applied on Tuesday. |
| `updated` | datetime | The date and time teams connector configuration was updated. |
| `wed` | boolean | Indicates whether or not the policy should be applied on Wednesday. |
