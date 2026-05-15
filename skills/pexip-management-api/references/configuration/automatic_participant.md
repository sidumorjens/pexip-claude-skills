# Automatically Dialed Participant

**Endpoint:** `/api/admin/configuration/v1/automatic_participant/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `alias` | string | The alias of the participant that is to be dialed when the conference starts. Maximum length: 250 characters. |
| `call_type` | string | Maximum media content of the call. The participant being called will not be able to escalate beyond the selected capability. |
| `conference` | `conference` (related resource) | The conference to which the Automatically Dialed Participant belongs. |
| `creation_time` | datetime | The time at which the Automatically Dialed Participant was created. |
| `description` | string | An optional description of the Automatically Dialed Participant. Maximum length: 250 characters. |
| `dtmf_sequence` | string | The DTMF sequence to be transmitted after the call to the automatically dialed participant starts. Insert a comma for a 2 second pause. Maximum length: 250 characters. |
| `id` | integer | The primary key. |
| `keep_conference_alive` | string | Determines whether the conference will continue when all other participants have disconnected. Yes: the conference will continue to run until this participant has disconnected (applies to Hosts only). If multiple: the conference will continue to run as long as there are two or more If multiple participants and at least one of them is a Host. No: the conference will be terminated automatically if this is the only remaining participant. |
| `presentation_url` | string | The optional RTMP URL for the second (presentation) stream. Maximum length: 250 characters. |
| `protocol` | string | The protocol to use when dialing the participant. Note that if the call is to a registered device, Pexip Infinity will instead use the protocol that the device used to make the registration. |
| `remote_display_name` | string | The optional user-facing display name for this participant, which will be shown in the participant lists. Maximum length: 250 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `role` | string | The level of privileges the participant will have in the conference. host: The participant will have full privileges. guest: The participant will have restricted privileges. |
| `routing` | string | Route this call manually using the defaults for the specified location - or route this call automatically using Call Routing Rules. |
| `streaming` | boolean | Identify the dialed participant as a streaming or recording device. |
| `system_location` | `system_location` (related resource) | For manually routed Automatically Dialed Participants (ADPs), this is the location of the Conferencing Node from which the call to the ADP will be initiated. For automatically routed ADPs, this is the notional source location used when considering if a routing rule applies or not - however the routing rule itself determines the location of the node that dials the ADP. To allow Pexip Infinity to automatically select the Conferencing Node to initiate the outgoing call, select Automatic. |
