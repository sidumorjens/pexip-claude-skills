# Pexip Entra Avatar Policy

A minimal Pexip Infinity **external policy server** that serves participant avatars by
looking up users in **Microsoft Entra ID** (Azure AD) via Microsoft Graph.

When a Pexip Conferencing Node needs an avatar for a participant, it issues an HTTP `GET`
to this server. The server:

1. Resolves the dialed alias to an Entra UPN (`sip:alice@contoso.com` → `alice@contoso.com`).
2. Fetches the user's profile photo from `GET /users/{upn}/photo/$value`.
3. Resizes it to the dimensions Pexip requested and returns `image/jpeg`.
4. Returns `404` if there's no photo (Pexip then falls back to a placeholder).

Only the **participant avatar** policy endpoint is implemented; leave the other request
types disabled on the Pexip Policy Profile (they fall through to Pexip's own database).

---

## Features

- **OAuth2 client-credentials** flow against Entra, with the access token cached in memory
  and proactively refreshed 60 seconds before expiry. A single-flight lock prevents
  thundering-herd refreshes, and a `401` from Graph forces one retry with a fresh token.
- **In-memory photo cache** keyed by UPN. TTL is configurable via `PHOTO_CACHE_TTL`.
  Negative results (user has no photo) are cached too so unknown users don't hammer Graph.
- **Tight upstream timeout** (4s) to stay within Pexip's 5-second policy budget.
- **HTTP Basic Auth** on the policy endpoint, credentials configured in `.env`.

---

## Requirements

- Python 3.10+
- An Entra **app registration** with the Microsoft Graph **`User.Read.All`** *Application*
  permission, admin-consented. (Application permission is required because the policy
  server acts on its own behalf, not on a user's behalf.)
- A Pexip Infinity deployment with a **Policy Profile** you can point at this server.

---

## Setup

From this directory:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Fill in ENTRA_TENANT_ID, ENTRA_CLIENT_ID, ENTRA_CLIENT_SECRET, POLICY_USER/PASS.

uvicorn app:app --host 0.0.0.0 --port 8080
```

### Configuration (`.env`)

| Variable | Purpose |
|---|---|
| `POLICY_USER` / `POLICY_PASS` | HTTP Basic credentials Pexip will use to call this server. Must match the Policy Profile. |
| `ENTRA_TENANT_ID` | The directory (tenant) ID from your Entra app registration. |
| `ENTRA_CLIENT_ID` | The application (client) ID. |
| `ENTRA_CLIENT_SECRET` | A client secret created for the app registration. |
| `PHOTO_CACHE_TTL` | How long (seconds) a photo or "no photo" result is cached before Graph is queried again. Default `3600`. |
| `LOG_LEVEL` | Standard Python log level. Default `INFO`. |

---

## Pexip configuration

In Pexip admin, under **Call control > Policy Profiles**:

1. Create (or edit) a Policy Profile.
2. Set the **Participant avatar URL** to `https://<your-host>/policy/` (Pexip appends
   `v1/participant/avatar/<alias>` to it).
3. Set the **Username** and **Password** to match `POLICY_USER` / `POLICY_PASS`.
4. Leave the other request types **disabled** unless you're extending this server.
5. Assign the Policy Profile to the system locations whose calls should use it.

> Pexip requires the policy server to respond within **5 seconds** and does **not**
> follow HTTP redirects. Terminate TLS at a reverse proxy (nginx / Caddy / ALB) in front
> of uvicorn in production — Pexip strongly prefers HTTPS.

---

## Endpoints

### `GET /policy/v1/participant/avatar/{alias}`

Pexip-facing. Requires HTTP Basic Auth.

- `alias` (path): the participant alias, possibly URI-scheme-prefixed (e.g.
  `sip:alice@contoso.com`). The server URL-decodes and strips the scheme and any SIP
  parameters before treating it as a UPN.
- `width`, `height` (query): the exact pixel size Pexip wants the JPEG returned at.

Returns:
- `200 image/jpeg` with the resized photo.
- `404` if the alias can't be resolved, the user has no photo, or anything goes wrong
  decoding the image. Pexip will use its placeholder.

### `GET /health`

Plain JSON `{"status": "ok"}`. Useful for load-balancer health checks.

---

## Testing locally

```bash
# Spin up
uvicorn app:app --host 0.0.0.0 --port 8080

# In another shell — fetch a real user's avatar
curl -u "$POLICY_USER:$POLICY_PASS" \
     -o /tmp/alice.jpg \
     "http://localhost:8080/policy/v1/participant/avatar/sip:alice@contoso.com?width=100&height=100"

file /tmp/alice.jpg     # should report: JPEG image data, 100x100
```

---

## Operational notes

- **Caches are in-process.** A restart drops the token and photo cache. That's fine for a
  single replica; if you scale horizontally, give each replica its own cache (it just
  means a few more Graph calls until each replica warms up). For shared caching across
  replicas, swap the dicts in [entra.py](entra.py) for Redis.
- **Pexip's 250-character response limit** doesn't apply here — that's for JSON policy
  responses. Avatar responses are raw bytes.
- **Color space:** Graph photos are usually JPEG/RGB, but Pillow's `convert("RGB")` in
  [app.py](app.py) safely handles RGBA / CMYK / grayscale inputs too. Pexip rejects
  CMYK JPEGs outright, so this conversion matters.
- **Logs** at `INFO` show each avatar request (alias, resolved UPN, requested size) and
  cache misses to Graph. Drop to `WARNING` in production once you're happy.

---

## File layout

```
app.py             FastAPI app + avatar endpoint + alias->UPN resolution
entra.py           OAuth2 token cache + Microsoft Graph photo client + photo cache
requirements.txt
.env.example       Template — copy to .env and fill in
.gitignore
```
