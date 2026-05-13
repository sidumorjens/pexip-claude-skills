# Pexip Subnet → Media Location Policy Server

Sample Pexip Infinity External Policy server. Maps participant IP subnets to
Pexip system locations for **media location** allocation; the other five
policy endpoints are stubbed to pass through to Pexip's database.

## Install & run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

POLICY_USER=pexip POLICY_PASS=changeme \
    uvicorn policy_server:app --host 0.0.0.0 --port 8080
```

Env vars:

| Var | Default | Purpose |
|---|---|---|
| `POLICY_USER` | `pexip` | HTTP Basic username Pexip will use |
| `POLICY_PASS` | `changeme` | HTTP Basic password |
| `SUBNET_MAP_PATH` | `subnet_map.json` | Path to the subnet → location map |

## Configure the subnet map

Edit [subnet_map.json](subnet_map.json). Each entry has:

- `subnet` — CIDR (IPv4 or IPv6). Longest prefix wins; order in the file does not matter.
- `location` — name of a Pexip system location (must exist in Infinity)
- `overflow_locations` — optional ordered list, used when the principal hits capacity
- `description` — optional, for humans

If no subnet matches, the participant gets `default_location` /
`default_overflow_locations`.

Reload without restarting:

```bash
curl -u pexip:changeme -X POST http://localhost:8080/admin/reload
```

> **Critical:** every location name (principal and overflow) **must** match a
> configured Pexip system location exactly. If any name is invalid, Pexip
> treats the entire response as failed and falls back to its own default
> allocation logic.

## Test without Pexip

Quick subnet-map lookup (no Pexip request shape, just the resolver):

```bash
curl -u pexip:changeme "http://localhost:8080/admin/lookup?ip=10.10.4.7"
# → {"ip":"10.10.4.7","matched_subnet":"10.10.0.0/16","location":"Oslo",
#    "overflow_locations":["Stockholm","London"]}

curl -u pexip:changeme "http://localhost:8080/admin/lookup?ip=10.30.5.42"
# → matches the more-specific 10.30.5.0/24 → Boston, not the /16 → New York
```

Simulate a real Pexip media-location request:

```bash
curl -u pexip:changeme \
  "http://localhost:8080/policy/v1/participant/location?\
call_direction=dial_in&protocol=webrtc&bandwidth=0&registered=False&\
trigger=invite&remote_display_name=Alice&remote_alias=alice@example.com&\
remote_address=10.20.1.5&remote_port=64410&location=London&\
node_ip=10.144.101.21&version_id=39&pseudo_version_id=77683.0.0&\
service_name=meet.alice&unique_service_name=meet.alice&local_alias=meet.alice"
```

Response:

```json
{
  "status": "success",
  "result": {
    "location": "Sydney",
    "overflow_locations": ["Singapore"]
  },
  "reason": "matched 10.20.0.0/16"
}
```

## Wire up in Pexip Infinity

1. **Call control > Policy Profiles > Add**
2. Set the base URL: `https://<your-host>/policy/v1`
3. Set HTTP Basic username/password matching `POLICY_USER` / `POLICY_PASS`
4. Enable **Apply external policy to participant media location**
5. Leave the other request types disabled (or enabled; they pass through here)
6. Assign the profile to the relevant system locations under
   **Platform > Locations**

In production, terminate TLS in front of this server (e.g. nginx) and use a
valid certificate chain — Pexip will not follow redirects and has a hard
5-second timeout per request.

## Endpoints summary

| Path | What it does |
|---|---|
| `GET /policy/v1/participant/location` | **Real logic** — subnet → location lookup |
| `GET /policy/v1/service/configuration` | Pass-through (`action: continue`) |
| `GET /policy/v1/participant/properties` | Pass-through |
| `GET /policy/v1/participant/avatar/{alias}` | 404 (use Pexip defaults) |
| `GET /policy/v1/registrations` | Empty list |
| `GET /policy/v1/registrations/{alias}` | Pass-through |
| `GET /health` | Liveness probe |
| `POST /admin/reload` | Reload `subnet_map.json` without restart |
| `GET /admin/lookup?ip=...` | Test the resolver directly |
