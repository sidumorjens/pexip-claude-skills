---
name: pexip-management-api
description: Expert knowledge for working with the Pexip Infinity Management Node REST API — the HTTP API exposed by the Conferencing Platform's Management Node under /api/admin/{configuration,status,command,history}/v1/. Use this skill whenever the user is querying or modifying VMRs (conferences), aliases, system locations, worker VMs, devices, automatic participants, identity providers, themes, or any other resource on a Pexip Management Node; controlling live participants (mute, disconnect, transfer, dial-out); reading live status (conferences in progress, participants connected, licensing, alarms); pulling call history; or building scripts/services that integrate with a Pexip Mgr Node. Also triggers for questions about Pexip resource field names, allowed methods, related resources, or "what does field X mean on resource Y". The full schema for 154 resources is shipped with this skill and indexed in references/INDEX.md — always consult it before answering, because field names and types differ subtly across the four namespaces.
---

# Pexip Infinity Management API skill

## What this skill is for

The Pexip Infinity Management Node exposes a Tastypie-style REST API at:

- `https://<mgr>/api/admin/configuration/v1/<resource>/` — read/write platform config (VMRs, aliases, locations, themes, devices, etc.)
- `https://<mgr>/api/admin/status/v1/<resource>/` — read live state (conferences, participants, licensing, alarms)
- `https://<mgr>/api/admin/command/v1/<resource>/<action>/` — trigger live actions (dial out, disconnect, mute, transfer, snapshot, backup)
- `https://<mgr>/api/admin/history/v1/<resource>/` — read post-call history records

JSON in, JSON out. List endpoints support filtering via Tastypie query params (`?name=foo`, `?id__in=1,2,3`, `?limit=200`, `?offset=400`).

### Auth

Three options, all over HTTPS:

- **HTTP Basic** — web-admin credentials (default username `admin`). Simplest, fine for scripts.
- **OAuth** — authenticate once, get a token with a TTL, reuse it until expiry. Best for high-frequency scripts that would otherwise hammer the auth path.
- **LDAP** — every request triggers a request to the LDAP server. Pexip recommends a **dedicated API service account** if you go this route. OAuth and LDAP can be combined.

## How to navigate the bundled schema

The full schema for all 154 resources is in [`references/`](references/):

1. **Always read [`references/INDEX.md`](references/INDEX.md) first** to find the resource(s) relevant to the user's question. The index lists every endpoint grouped by namespace with its human-readable title.
2. **Then read the specific resource file** (e.g. `references/configuration/conference.md`) for its allowed methods, full field list, types, and per-field descriptions.
3. Resources marked `(related resource)` in the type column refer to another resource — follow the link to that resource's file if you need the embedded shape.

Do not assume field names — confirm them in the schema file before writing example payloads. Pexip field names are inconsistent across namespaces (e.g. `name` vs `local_alias`, `service_tag` vs `tag`).

## Auth and request patterns

```bash
# List, with auth
curl -u admin:pass -H "Accept: application/json" \
  "https://mgr.example.com/api/admin/configuration/v1/conference/?limit=10"

# Get one resource
curl -u admin:pass \
  "https://mgr.example.com/api/admin/configuration/v1/conference/42/"

# Create (POST)
curl -u admin:pass -H "Content-Type: application/json" -X POST \
  -d '{"name":"my-vmr","service_type":"conference",...}' \
  "https://mgr.example.com/api/admin/configuration/v1/conference/"
# 201 Created; Location header has the new resource URI

# Partial update (PATCH)
curl -u admin:pass -H "Content-Type: application/json" -X PATCH \
  -d '{"description":"updated"}' \
  "https://mgr.example.com/api/admin/configuration/v1/conference/42/"

# Command (always POST, body is the action's parameters)
curl -u admin:pass -H "Content-Type: application/json" -X POST \
  -d '{"conference":"my-vmr","destination":"alice@example.com","protocol":"sip","role":"guest"}' \
  "https://mgr.example.com/api/admin/command/v1/participant/dial/"
```

### List response shape

List endpoints wrap results in a Tastypie envelope:

```json
{
  "meta": {
    "limit": 20,
    "offset": 0,
    "total_count": 137,
    "next": "/api/admin/configuration/v1/conference/?limit=20&offset=20",
    "previous": null
  },
  "objects": [ { "id": 1, "name": "...", "resource_uri": "...", ... }, ... ]
}
```

Single-resource `GET /<resource>/<id>/` returns the resource object directly (no envelope). Default page size is small — paginate with `?limit=N&offset=M` (or `?limit=0` for "all", though discouraged on large resources). Always follow `meta.next` rather than guessing offsets.

### Bulk operations via PATCH

`PATCH` against a **list** endpoint (no ID) lets you create, update, and delete many objects in one request:

```json
{
  "objects": [
    { "name": "VMR_1", "service_type": "conference" },
    { "name": "VMR_2", "service_type": "conference" },
    { "resource_uri": "/api/admin/configuration/v1/conference/42/", "description": "renamed" }
  ],
  "deleted_objects": [
    "/api/admin/configuration/v1/conference/5/",
    "/api/admin/configuration/v1/conference/6/"
  ]
}
```

Rules: objects to **update** must include `resource_uri`; objects to **create** must omit it. `deleted_objects` is a list of resource URIs. PATCH may return `202 Accepted` for async operations — the change is queued, not necessarily complete on response.

## Gotchas worth knowing before answering

- **Trailing `/` is mandatory** on every path. `/api/admin/configuration/v1/conference/42/` works; `/api/admin/configuration/v1/conference/42` does not. Query strings after `?` don't need it.
- **`DELETE` on a list URI wipes the entire collection.** `DELETE /api/admin/configuration/v1/conference/` deletes every VMR. Always include an ID. Confirm with the user before any DELETE you generate.
- **`PUT` is destructive** — it replaces all objects under the URI. Pexip explicitly recommends against it; use `PATCH` for partial updates.
- **Rate limit: 1,000 requests / 60 seconds** per Management Node. Bulk PATCH counts as one request — prefer it over loops of individual writes when changing many resources.
- **Don't use this API for real-time call-admission control.** Heavy use causes DB locking and CPU pressure across the deployment. Pexip's explicit guidance: use **External Policy** (per-call decisions) or **Event Sinks** (post-event capture) for the hot path.
- **Configuration replication lag**: changes take ~1 minute to propagate to Conferencing Nodes (longer in deployments with 60+ nodes). A `POST` that returns 201 is committed on the Mgr Node but not necessarily live on the Conferencing Nodes yet — don't immediately dial into a VMR you just created.

- **`POST` vs `PATCH` vs `PUT`**: `POST` creates, `PATCH` partial-updates, `PUT` full-replaces (must include every required field). Use `PATCH` for most "change one field" tasks — it's safer.
- **Sub-resources** like `/api/admin/status/v1/participant/<id>/media_stream/` are read-only per-call media-stream stats; they are not at the top level. Their schemas live in files like `references/status/participant__media_stream.md`.
- **Command endpoints take the resource by name or ID** depending on the action — check the schema. `participant/disconnect/` takes participant IDs; `participant/dial/` takes a conference name plus destination.
- **History endpoints are eventually consistent** — a call that just ended may take seconds to appear in `/api/admin/history/v1/participant/`.
- **Tastypie filter operators**: `__in`, `__icontains`, `__startswith`, `__gte`, `__lte`, etc. Example: `?start_time__gte=2026-01-01T00:00:00`.
- **`/api/admin/status/v1/licensing/`** is the canonical place to check Audio/Connect/Meeting Room license usage — don't infer from worker VM counts.
- **VMR = `conference` resource.** The web UI calls them "Virtual Meeting Rooms" but the API resource is named `conference`. Users frequently get this wrong — when they say "VMR" or "meeting room", they mean `configuration/conference/`.
- **Aliases are a separate resource.** A VMR's dial-in addresses live in `configuration/conference_alias/` with an FK back to the conference, not as a list field on the conference itself.
- The HTML page at `/admin/platform/schema/` (used to generate `references/`) is the **most complete** source of field descriptions — much more detailed than the per-resource `/schema/` JSON endpoints, which only return field types.

## Regenerating the schema (next Pexip version)

When the Management Node is upgraded:

1. Log into `https://<mgr>/admin/platform/schema/` in a browser.
2. Save the page as `API Schemas _ Pexip Infinity.html` in the skill root (overwriting the existing one).
3. Run `python3 scripts/parse_schema.py` — this rebuilds the entire `references/` tree.

The parser uses only the Python stdlib (no deps). Output should be 149 resources + 4 embedded + 1 response = 154 total.

## Official docs (Pexip)

- [Using the management API](https://docs.pexip.com/api_manage/using.htm) — auth options, rate limit
- [Configuration API](https://docs.pexip.com/api_manage/api_configuration.htm) — bulk operations, examples
- [Status API](https://docs.pexip.com/api_manage/api_status.htm)
- [Command API](https://docs.pexip.com/api_manage/api_command.htm)
- [Extracting and analyzing call data](https://docs.pexip.com/api_manage/extract_analyse.htm) — history API patterns
- [Using OAuth](https://docs.pexip.com/admin/managing_API_oauth.htm)
- [Using an LDAP database](https://docs.pexip.com/admin/managing_admin_ldap.htm)
- [Event sinks](https://docs.pexip.com/admin/event_sink.htm) — for real-time push (use instead of polling status)

## When NOT to use this skill

- For working with **Pexip Event Sinks** (the webhook *receiver* side that Pexip pushes events to) — use the `pexip-event-sink` skill.
- For **External Policy server** development (Pexip calling out to your policy service for routing decisions) — use the `pexip-external-policy` skill.
- For **client-side / Pexip Web App / Infinity Connect** development — these use the participant API (`/api/client/v2/`), not the Management API. This skill does not cover that surface.
