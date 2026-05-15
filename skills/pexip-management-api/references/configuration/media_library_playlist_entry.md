# Media Playlist Item

**Endpoint:** `/api/admin/configuration/v1/media_library_playlist_entry/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `entry_type` | string | Type of entry referred to by playlist entry |
| `id` | integer | The primary key. |
| `media` | `media_library_entry` (related resource) | A single related resource. Can be either a URI or set of nested resource data. |
| `playcount` | integer | The number of times the item is played, the default is 1. If you set the value to 0 the item plays repeatedly until the user disconnects themselves or until the call is terminated programmatically via the management API. |
| `playlist` | `media_library_playlist` (related resource) | A single related resource. Can be either a URI or set of nested resource data. |
| `position` | integer | Every item must have a unique position specified. This refers to the order in which in the Media Library Item is played relative to the other items in the playlist. Please note that Position is only used when shuffle is off. |
| `resource_uri` | string | The URI that identifies this resource. |
