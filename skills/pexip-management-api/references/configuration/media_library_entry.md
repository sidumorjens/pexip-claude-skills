# Media Library Item

**Endpoint:** `/api/admin/configuration/v1/media_library_entry/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `description` | string | A description of this Media Library Item. Maximum length: 1024 characters. |
| `file_name` | string | The file name of the media uploaded |
| `id` | integer | The primary key. |
| `media_file` | file | The media to upload. Only MP4 video files with H.264 encoding are supported. |
| `media_format` | string | Indicates the media format |
| `media_size` | integer | Indicates the size of the uploaded media |
| `media_type` | string | Indicates the media type. |
| `name` | string | The name used to refer to this Media Library Item. Maximum length: 1024 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `uuid` | string | The UUID for the Media Library Item |
