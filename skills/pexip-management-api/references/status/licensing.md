# Licensing status

**Endpoint:** `/api/admin/status/v1/licensing/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `audio_count` | integer | The concurrent count of reserved audio port licenses. |
| `audio_total` | integer | The total number of audio port licenses. |
| `customlayouts_active` | boolean | Number of Custom Layouts feature licenses |
| `ghm_count` | integer | The number of Google Meet interoperability licenses in use. |
| `ghm_total` | integer | The total number of Google Meet interoperability licenses. |
| `googletrustedjoin_active` | boolean | Number of Google Trusted Join feature licenses |
| `otj_count` | integer | The count of reserved OTJ Endpoint licenses. |
| `otj_total` | integer | The total number of OTJ Endpoint licenses. |
| `port_count` | integer | The concurrent count of reserved port licenses. |
| `port_total` | integer | The total number of port licenses. |
| `scheduling_count` | integer | The number of scheduling licences in use. |
| `scheduling_total` | integer | The total number of scheduling licenses. |
| `system_count` | integer | The concurrent count of reserved system licenses. |
| `system_total` | integer | The total number of system licenses |
| `teams_count` | integer | The number of Microsoft Teams interoperability licenses in use. |
| `teams_total` | integer | The total number of Microsoft Teams interoperability licenses. |
| `telehealth_count` | integer | The number of Epic Telehealth integration licenses in use. |
| `telehealth_total` | integer | The total number of Epic Telehealth integration licenses. |
| `vmr_count` | integer | The number of configured services consuming vmr licenses. |
| `vmr_total` | integer | The total number of vmr licenses. |
| `zoomtrustedjoin_active` | boolean | Number of Zoom Trusted Join feature licenses |
