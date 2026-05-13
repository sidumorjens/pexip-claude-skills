# Participant Avatar — Full Field Reference

**Request URI:** `GET /policy/v1/participant/avatar/<alias>`

Returns a JPEG image representing a conference participant or directory contact. The `<alias>` in the URL path is the alias whose avatar is required (may include scheme, e.g. `sip:alice@example.com` — your server must parse this).

**Critical:** This is the **only** policy endpoint that does NOT return JSON. It returns a JPEG image. If a valid JPEG isn't returned or the image is the wrong size, Pexip returns 404 to the requesting app, which then uses a placeholder image.

---

## Two distinct call paths

There are two paths that lead to an avatar request, and the **set of parameters included differs**:

1. **Service participant context** — a participant is in a call, and the app needs to display their avatar.
   - All the common parameters are included (alias, role, service info, etc.)

2. **Directory information context** — a participant just got a directory list and the app needs to display avatars for the entries.
   - Only a minimal set of parameters is included (marked with * below).

---

## Request Parameters

| Parameter | Description |
|---|---|
| `bandwidth` | The maximum requested bandwidth for the call. |
| `call_direction` | `"dial_in"`, `"dial_out"`, or `"non_dial"`. |
| `call_tag` | An optional call tag. |
| `has_authenticated_display_name` | Boolean. |
| `height` * | Required height in pixels of the image to be returned. |
| `idp_uuid` | UUID of the IdP. |
| `local_alias` | The originally-dialed incoming alias. |
| `location` * | Pexip system location of the Conferencing Node. |
| `ms-subnet` † | SIP only. |
| `node_ip` * | IP of the Conferencing Node. |
| `p_Asserted-Identity` † | SIP only. |
| `protocol` | `"api"`, `"webrtc"`, `"sip"`, `"rtmp"`, `"h323"`, `"teams"`, `"mssip"`. |
| `proxy_node_address` | Proxying Edge Node address (if applicable). |
| `proxy_node_location` | Proxying Edge Node location (if applicable). |
| `pseudo_version_id` * | Pexip build number. |
| `registered` * | Boolean. |
| `remote_address` | IP of the participant. |
| `remote_alias` | Participant alias (also in the URL path). |
| `remote_display_name` | Display name. |
| `remote_port` | IP port. |
| `role` | `"chair"`, `"guest"`, or `"unknown"` (at PIN entry or Waiting for Host). |
| `service_name` | Service name. |
| `service_tag` | Service tag. |
| `supports_direct_media` | Boolean. |
| `teams_tenant_id` | Teams tenant ID. |
| `trigger` | Policy trigger. |
| `unique_service_name` | Unique service identifier. |
| `vendor` | Endpoint system details. |
| `version_id` * | Pexip software version. |
| `width` * | Required width in pixels of the image to be returned. |

> * These are the only parameters included when the avatar request is from a **directory information** lookup (rather than a participant in a service).
> † SIP-triggered requests only.

### Example: avatar for a WebRTC participant in a conference

```
GET /example.com/policy/v1/participant/avatar/alice
  ?protocol=webrtc
  &node_ip=10.44.99.2
  &service_name=meet.bob
  &registered=False
  &remote_address=10.44.75.250
  &version_id=35
  &service_tag=
  &bandwidth=0
  &pseudo_version_id=77683.0.0
  &vendor=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36
  &height=100
  &unique_service_name=meet.bob
  &local_alias=meet.bob
  &remote_port=58426
  &idp_uuid=
  &has_authenticated_display_name=False
  &supports_direct_media=False
  &call_direction=dial_in
  &remote_alias=alice
  &remote_display_name=Alice
  &width=100
  &trigger=invite
  &role=chair
  &location=London
```

### Example: avatar triggered by a previous directory information lookup

```
GET /example.com/policy/v1/participant/avatar/alice
  ?node_ip=10.47.2.46
  &registered=True
  &version_id=35
  &height=40
  &width=40
  &location=London
  &pseudo_version_id=77683.0.0
```

---

## Response Requirements

- **Content-Type:** `image/jpeg`
- **Color space:** RGB or RGBA (CMYK is **NOT** supported)
- **Dimensions:** Must match the requested `width` and `height` exactly

If any of these are wrong, Pexip returns 404 to the client and a placeholder image is used.

### Fallback to placeholder (404)

If you don't have an avatar for the alias, return HTTP 404 (don't try to return a "blank" JPEG):

```python
return Response(status_code=404)
```

---

## Worked Example: Microsoft Graph / Entra ID Avatar Proxy

```python
import io
import httpx
from PIL import Image
from fastapi import HTTPException
from fastapi.responses import Response

@app.get("/policy/v1/participant/avatar/{alias:path}")
async def participant_avatar(alias: str, request: Request, _=Depends(check_auth)):
    width = int(request.query_params.get("width", 100))
    height = int(request.query_params.get("height", 100))

    # Strip SIP scheme
    if alias.startswith("sip:"):
        alias = alias[4:]

    # Look up photo from Microsoft Graph (caches token, etc.)
    photo_bytes = await fetch_graph_photo(alias)
    if not photo_bytes:
        return Response(status_code=404)

    # Resize to requested dimensions
    img = Image.open(io.BytesIO(photo_bytes))
    if img.mode == "CMYK":
        img = img.convert("RGB")
    elif img.mode == "RGBA":
        img = img.convert("RGB")  # Pexip wants RGB or RGBA, RGB is safest
    img = img.resize((width, height), Image.Resampling.LANCZOS)

    out = io.BytesIO()
    img.save(out, format="JPEG", quality=85)
    return Response(content=out.getvalue(), media_type="image/jpeg")
```

### Tips for production avatar serving

1. **Cache aggressively.** The same alias is requested many times; cache by `(alias, width, height)`.
2. **Cache photo bytes too.** Don't hit the upstream (Graph/LDAP) on every request.
3. **Use Lanczos for resizing** — Pillow's default `BILINEAR` looks rough at small sizes.
4. **Handle the alias scheme.** SIP aliases include `sip:`; SfB may include `sip:` or have `;tag=`; WebRTC aliases often don't.
5. **Bound the upstream call** with a tight timeout (1-2s) — the 5s Pexip budget is shared with your lookup.
6. **CMYK → RGB conversion** is the most common image-format trap. JPEGs from cameras are often CMYK.
