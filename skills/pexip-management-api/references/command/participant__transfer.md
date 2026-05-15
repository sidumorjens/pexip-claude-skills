# /api/admin/command/v1/participant/transfer/

**Endpoint:** `/api/admin/command/v1/participant/transfer/`

## Allowed methods

- **Allowed Methods (list):** POST

## Fields

| Field | Type | Description |
|---|---|---|
| `conference_alias` | string | The alias of the conference to which the participant should be transferred. Maximum length: 250 characters. |
| `participant_id` | string | The unique identifier of the participant to be transferred. Maximum length: 200 characters. |
| `role` | string | The level of privileges the participant will have in the conference. |
