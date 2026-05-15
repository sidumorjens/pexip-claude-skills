# SIP credential

**Endpoint:** `/api/admin/configuration/v1/sip_credential/`

## Allowed methods

- **Allowed Methods:** GET, POST, PUT, DELETE, PATCH

## Fields

| Field | Type | Description |
|---|---|---|
| `id` | integer | The primary key. |
| `password` | string | The password to use in responding to a SIP authentication challenge for the given realm. Maximum length: 100 characters. |
| `realm` | string | The realm defines the protection space of the host or proxy (such as its name or domain, e.g. sipproxy.example.com) that is challenging Pexip Infinity for authentication. Maximum length: 255 characters. |
| `resource_uri` | string | The URI that identifies this resource. |
| `username` | string | The username to use in responding to a SIP authentication challenge for the given realm. Maximum length: 100 characters. |
