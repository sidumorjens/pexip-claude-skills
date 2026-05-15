# Alias

**Endpoint:** `/api/admin/configuration/v1/conference_alias/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `alias` | string | The dial string used to join this service, in the form that it will be received by Pexip Infinity. This alias must include any domain that is automatically added by the participant's endpoint or call control system, or dialed by the participant. Maximum length: 250 characters. |
| `conference` | `conference` (related resource) | A single related resource. Can be either a URI or set of nested resource data. |
| `creation_time` | datetime | The time at which the alias was created. |
| `description` | string | An optional description of the alias. Note that this description may be displayed to end users on registered Pexip apps who are performing a directory search. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `resource_uri` | string | The URI that identifies this resource. |
| `view_order` | integer | The order in which to display this conference alias. |
