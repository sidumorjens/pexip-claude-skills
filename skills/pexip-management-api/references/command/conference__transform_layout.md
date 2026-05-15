# /api/admin/command/v1/conference/transform_layout/

**Endpoint:** `/api/admin/command/v1/conference/transform_layout/`

## Allowed methods

- **Allowed Methods (list):** POST

## Fields

| Field | Type | Description |
|---|---|---|
| `ai_enabled_indicator` | boolean | Whether the AI enabled indicator is present in the conference. |
| `conference_id` | string | The unique identifier of the conference to transform layout. Maximum length: 200 characters. |
| `enable_overlay_text` | boolean | If enabled, the display name or alias will be shown for each participant. |
| `free_form_overlay_text` | string | A custom display name to show for the first participant.Maximum length: 1000 characters. |
| `guest_layout` | string | The guest layout to apply to this conference. |
| `host_layout` | string | The host layout to apply to this conference. |
| `layout` | string | The layout to apply to this conference. |
| `live_captions_indicator` | boolean | Whether the live captions indicator is present in the conference. |
| `plus_n_pip_enabled` | boolean | Whether the 'plus n indicator' i.e. the number of participants present in the conference, is displayed. |
| `recording_indicator` | boolean | Whether the recording indicator is present in the conference. |
| `streaming_indicator` | boolean | Whether the streaming indicator is present in the conference. |
| `transcribing_indicator` | boolean | Whether the transcribing indicator is present in the conference. |
