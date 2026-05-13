# Directory Information — Full Field Reference

**Request URI:** `GET /policy/v1/registrations`

Provides phonebook entries to Pexip apps that are registered to a Pexip Infinity Conferencing Node. Triggered when the registered user types into the directory search field in the app.

---

## Request Parameters

| Parameter | Description |
|---|---|
| `call_tag` | An optional call tag assigned to a participant. |
| `limit` | Maximum number of results to return (currently always set to `10`). |
| `location` | Pexip system location of the Conferencing Node making the request. |
| `node_ip` | IP of the Conferencing Node. |
| `pseudo_version_id` | Pexip build number. |
| `q` | The string the user typed — what to look up in the directory. |
| `registration_alias` | The alias of the registered client performing the lookup. |
| `version_id` | Pexip software version. |

### Example GET request

```
GET /example.com/policy/v1/registrations
  ?q=ali
  &registration_alias=bob@example.com
  &limit=10
  &location=london
  &node_ip=10.44.155.21
  &pseudo_version_id=77683.0.0
  &version_id=35
```

---

## Response Envelope

```json
{
  "status": "success",
  "result": [ <directory_data> ],
  "ignore_local": false
}
```

> Unlike most other request types, `result` is a **list of objects**, not a single object. The list is also expected to be **pre-sorted** by the policy server — Pexip presents the entries in the order you return them.

### Top-level fields

| Field | Required | Type | Description |
|---|---|---|---|
| `status` | Yes | String | Must be `"success"`. |
| `result` | Yes | List | Sorted list of directory entries (see below). |
| `ignore_local` | No | Boolean | If `true`, Pexip ignores aliases of local services/devices in the response. If `false` (default), Pexip merges local aliases with the policy-server-returned list. |

### Entry fields (each object in `result`)

| Field | Required | Description |
|---|---|---|
| `alias` | Yes | Alias of the device or VMR. Pexip will use this as the `<alias>` in subsequent avatar requests, and the alias the Pexip app will dial. |
| `description` | Yes | Description or name associated with the alias. |
| `username` | Yes | Username associated with the device/VMR. Currently unused by Pexip but must be included (may be empty string). |

---

## Worked Examples

### Two matching directory entries

```json
{
  "status": "success",
  "result": [
    {
      "username": "alice",
      "alias": "alice@example.com",
      "description": "Alice's VMR"
    },
    {
      "username": "bob",
      "alias": "bob@example.com",
      "description": "Bob's VMR"
    }
  ]
}
```

### Return nothing and tell Pexip to ignore local aliases too

(Use this to completely suppress directory information from a particular registered user.)

```json
{
  "status": "success",
  "result": [],
  "ignore_local": true
}
```

### Implementation: search a corporate directory

```python
@app.get("/policy/v1/registrations")
async def directory_information(request: Request, _=Depends(check_auth)):
    params = request.query_params
    query = params.get("q", "").strip()
    limit = int(params.get("limit", 10))
    requester = params.get("registration_alias", "")

    if not query:
        return JSONResponse({"status": "success", "result": []})

    # Filter / ACL based on the requester (only show contacts visible to them)
    results = await search_directory(query, requester, limit=limit)

    entries = [
        {
            "username": r.username or "",
            "alias": r.sip_address,
            "description": r.display_name,
        }
        for r in results
    ]

    return JSONResponse({
        "status": "success",
        "result": entries,
        "ignore_local": False  # also include locally configured VMRs
    })
```

### Empty / no-match response (fall back to local DB)

```json
{
  "status": "success",
  "result": []
}
```

With `ignore_local` defaulting to `false`, this means "I have no policy entries to add; just use Pexip's local database."

---

## Performance Notes

- The 5-second timeout applies here too. Search results from LDAP or large directories should be cached.
- `q` may be very short (1-2 characters as the user types). Either implement debounced searches client-side (not your option — Pexip controls this) or cache prefix searches.
- Return at most `limit` (10) entries; returning more is wasteful and may be ignored.
- Sort by relevance: exact matches first, then prefix matches, then substring matches.
