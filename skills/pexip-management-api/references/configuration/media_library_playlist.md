# Media Playlist

**Endpoint:** `/api/admin/configuration/v1/media_library_playlist/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `description` | string | A description of this Media Playlist. Maximum length: 1024 characters. |
| `id` | integer | The primary key. |
| `loop` | boolean | If enabled, for a given call the whole playlist is repeated until the user disconnects themselves or until the call is terminated programmatically via the management API. |
| `name` | string | The name used to refer to this Media Playlist. Maximum length: 1024 characters. |
| `playlist_entries` | `media_library_playlist_entry` (related resource) | Many related resources. Can be either a list of URIs or list of individually nested resource data. |
| `resource_uri` | string | The URI that identifies this resource. |
| `shuffle` | boolean | If enabled, the playlist is shuffled so that all media items are played in a random order (media items’ specified positions are not used). |
