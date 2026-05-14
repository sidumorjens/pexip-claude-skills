---
name: pexip-event-sink
description: >
  Expert knowledge for designing, building, and operating Pexip Infinity Event
  Sink receivers — the HTTP webhook endpoints Pexip pushes conference,
  participant, presentation, recording, and transcript events to. Use this
  skill whenever the user is working with Pexip Event Sinks, building a webhook
  receiver for Pexip, ingesting Pexip events into a queue/database/BI system,
  implementing call detail record (CDR) capture, building real-time conference
  dashboards, archiving call metadata, or debugging missing/duplicated event
  deliveries. Also triggers for questions about event payload shapes, retry
  semantics, idempotency, ordering guarantees, scaling event sink receivers,
  or correlating events into call records. Use this skill — Pexip event sinks
  have several silent failure modes and the operational patterns (idempotency,
  fast ACK, durable persistence) matter more than the wire protocol itself.
---

# Pexip Infinity Event Sinks — Expert Skill

Practical knowledge for receiving and processing **Pexip Infinity Event Sink** payloads — the
push-based webhook stream Pexip emits for conference and participant lifecycle events,
presentations, recording, and (depending on version) transcripts and other system signals.

Unlike External Policy (which is request/response and blocks the call), Event Sinks are
**fire-and-forget** from Pexip's side: it POSTs JSON, expects a fast `2xx`, and moves on.
That apparent simplicity hides the bits that matter — retry behaviour, ordering, duplicates,
and what happens when your receiver is slow. This skill covers both the protocol and the
operational patterns that keep an event-sink integration trustworthy over time.

> ⚠️ **Verify against your Pexip version:** Pexip Infinity's event sink event set, payload
> field names, and retry semantics evolve between releases. This skill captures the stable
> patterns and the field-tested operational shape; for the **exact** payload schema your
> deployment emits, cross-check against
> `https://docs.pexip.com/admin/event_sink.htm` (or the relevant page for your version)
> and ideally a captured sample from your environment.

---

## Quick Decision Tree

| Goal | Read this first |
|---|---|
| Understand conference lifecycle events (start/update/end) | `references/conference-events.md` |
| Understand participant lifecycle events (join/update/leave) | `references/participant-events.md` |
| Build a receiver from scratch | §3 below |
| Make the receiver durable, idempotent, scalable | §4 below |
| Integrate into billing / BI / archive / real-time dashboards | §5 below |
| Debug missing or duplicated events | §6 below |
| Pre-flight a new receiver before plugging it into Pexip | §7 below |

Each reference file contains the event-type-specific payload fields, expected
firing conditions, and worked examples. The body of this SKILL.md covers the
shared concepts and operational patterns that aren't in the docs.

---

## 1. How Pexip Event Sinks Work

A Pexip Conferencing Node sends an HTTP **POST** with a JSON body to your event-sink URL
whenever a lifecycle event occurs. Your server's job is to **acknowledge fast** (return
`2xx` quickly) and process the payload — durably — out of band.

### Transport & Auth

- **HTTP POST** (note: External Policy uses GET; Event Sinks use POST)
- **Content-Type:** `application/json`
- **HTTPS strongly recommended** in production
- **HTTP Basic Auth** is the standard auth mechanism (username/password configured per sink)
- Pexip discards your response **body** — only the status code matters
- One sink URL receives **all enabled event types**; the event type is in the JSON payload

> ⚠️ **Verify:** Some Pexip versions support additional auth options (client certificates,
> custom headers); HMAC payload signing is **not** a standard feature as of recent versions
> but check your version's release notes if you need cryptographic integrity.

### Configuration (in Pexip admin)

> ⚠️ **Verify path against your Pexip version.** Event sinks are typically configured under
> **Platform > Locations > [Location] > Event Sinks**, or globally under
> **Call control > Event Sinks**. Each sink has:
>
> - URL
> - Basic Auth username/password
> - Per-event-type enable toggles (you can opt out of categories you don't need)
> - Verification mode (test connection from Pexip admin UI)

Multiple sinks can be configured. Every enabled sink receives every enabled event — useful
for separate billing + BI receivers, or for a passive archive alongside a live consumer.

### Delivery semantics

| Property | Behaviour |
|---|---|
| **Delivery** | At-least-once. Duplicates are possible — design for idempotency. |
| **Ordering** | No global ordering. Per-conference ordering is **not guaranteed** in the general case; correlate by timestamp + `conference_uuid` rather than arrival order. |
| **Retries** | Pexip retries on non-2xx and on timeout. ⚠️ **Verify** exact count + backoff for your version — typical behaviour is a small number of retries with short backoff, then drop. |
| **Timeouts** | ⚠️ **Verify** — Pexip imposes a short per-request timeout (low single-digit seconds). Slow receivers are treated as failures. |
| **Persistence on Pexip side** | None to rely on. If your receiver is down for an extended period, events emitted during the outage may be lost. Build your receiver for HA. |
| **Backpressure** | Pexip will not slow down to match a slow receiver. Either ACK fast and queue, or accept dropped events. |

### Common payload envelope

Most event types share a common skeleton:

```json
{
  "event": "<event_name>",
  "version": "<schema_version>",
  "data": {
    "conference_uuid": "...",
    "timestamp": "...",
    "...": "..."
  }
}
```

> ⚠️ **Verify:** Field names (e.g. `event` vs. `name`, top-level vs. nested under `data`)
> differ between Pexip versions. The references in this skill describe the **conceptual**
> shape; treat them as a guide, not a contract.

### A note on what's pushed vs. polled

Event sinks push **lifecycle events**. They are **not**:

- A live participant roster (use the Management API `status/v1/participant/`)
- A real-time media-quality stream (that's a separate feed)
- A way to control calls (use the Management API for mid-call actions)

If your use case needs real-time control, combine event sinks (for state changes) with
Management API calls (for actions you want to take in response).

---

## 2. Event Types

Pexip emits several classes of event. The two most commonly integrated against — and the
two with reference files in this skill — are conference lifecycle and participant
lifecycle.

| Class | Typical events | Reference |
|---|---|---|
| **Conference lifecycle** | `conference_started`, `conference_updated`, `conference_ended` | `references/conference-events.md` |
| **Participant lifecycle** | `participant_connected`, `participant_updated`, `participant_disconnected` | `references/participant-events.md` |

> ⚠️ **Other event classes likely exist in your Pexip version** — presentation start/stop,
> recording lifecycle, transcript fragments, system alarms, and similar. Their availability
> and payload shape depend on the Pexip version and on which features (recording, AIMS,
> transcription) are licensed and configured. Check Pexip's official docs for the full list
> in your version; reference files for these classes can be added to this skill as your
> deployments need them.

### Correlating events into a call record

A typical CDR (Call Detail Record) or analytics row is built by joining:

- One `conference_started` and one `conference_ended` per conference (matched on `conference_uuid`)
- N `participant_connected` and N `participant_disconnected` per conference (matched on `participant_uuid`)
- Optional `*_updated` events for state changes mid-call (role change, alias change, etc.)

The receiver pattern in §4 (durable append-only log + idempotency by event UUID + downstream
aggregation) is what makes this correlation robust against duplicate delivery and out-of-order
arrival.

---

## 3. Implementing a Receiver

### Minimal FastAPI skeleton

The key principle: **ACK fast, process asynchronously**. Returning `200 OK` quickly stops
Pexip retrying; the actual work happens off the request thread.

```python
import asyncio
import logging
import os
import secrets

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("event-sink")

SINK_USER = os.environ["SINK_USER"]
SINK_PASS = os.environ["SINK_PASS"]

app = FastAPI()
security = HTTPBasic()

# Off-thread processing queue (swap for Redis/SQS/Kafka in production — see §4)
event_queue: asyncio.Queue = asyncio.Queue(maxsize=10_000)


def check_auth(credentials: HTTPBasicCredentials = Depends(security)) -> None:
    ok = (secrets.compare_digest(credentials.username, SINK_USER) and
          secrets.compare_digest(credentials.password, SINK_PASS))
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
        )


@app.post("/events")
async def receive_event(request: Request, _: None = Depends(check_auth)):
    payload = await request.json()
    # Minimal validation only — anything that lets us safely route + log
    event_type = payload.get("event") or payload.get("name") or "<unknown>"
    log.info("RX event=%s size=%d", event_type, len(await request.body() or b""))

    # ACK immediately; defer real processing
    try:
        event_queue.put_nowait(payload)
    except asyncio.QueueFull:
        # Don't 5xx — Pexip will retry and pile up duplicates.
        # Better to ACK and log loudly that we're shedding load.
        log.error("event_queue FULL — dropping event=%s", event_type)

    return {"status": "ok"}


@app.get("/health")
async def health():
    return {"status": "ok", "queue_depth": event_queue.qsize()}


@app.on_event("startup")
async def _start_worker():
    asyncio.create_task(_worker())


async def _worker():
    while True:
        payload = await event_queue.get()
        try:
            await process(payload)
        except Exception:
            log.exception("processing failed event=%s",
                          payload.get("event") or payload.get("name"))
        finally:
            event_queue.get_nowait if False else event_queue.task_done()


async def process(payload: dict) -> None:
    """Real persistence + side effects go here (see §4 for patterns)."""
    log.info("processed event=%s", payload.get("event") or payload.get("name"))
```

Notes:

- **One endpoint receives all event types.** Route by `payload["event"]` inside the handler
  (or inside `process()`).
- **Return 200 even on queue-full.** Pexip retrying a flood that you can't store is worse
  than dropping it — alarm on queue depth instead.
- **Defer all I/O** (DB writes, downstream HTTP calls) into the worker. The request handler
  must not block.

### Per-event-type routing

Once events are off the request thread, dispatch by event name. Use a small registry:

```python
HANDLERS = {}

def handler(event_name: str):
    def deco(fn):
        HANDLERS[event_name] = fn
        return fn
    return deco

@handler("conference_started")
async def on_conf_start(payload: dict):
    ...

@handler("participant_connected")
async def on_p_connect(payload: dict):
    ...

async def process(payload: dict) -> None:
    name = payload.get("event") or payload.get("name")
    fn = HANDLERS.get(name)
    if fn is None:
        log.warning("no handler for event=%s — payload dropped after persist", name)
        return
    await fn(payload)
```

> Always **persist before dispatch.** If a handler is missing or fails, the raw event must
> still be in your durable log so you can replay it once the handler exists.

### Docker Compose pattern

```yaml
services:
  event-sink:
    build: .
    environment:
      - SINK_USER=pexip
      - SINK_PASS=changeme
      - DATABASE_URL=postgresql://...
    expose:
      - "8080"

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - event-sink
```

The HTTPS termination point (nginx, Caddy, your cloud LB) **must not** transform 5xx into
2xx — let Pexip see real failures so it retries.

---

## 4. Operational Patterns

The wire protocol is a small part of the work. These patterns are what separate a working
event-sink integration from a flaky one.

### Idempotency — the most important pattern

Pexip retries on non-2xx and on timeout. Slow handlers, transient network errors, and your
own crashes all cause **duplicate deliveries**. Design every handler to be safe to run
multiple times on the same payload.

Two reliable approaches:

```python
# 1. Dedup at ingest by event identifier
async def process(payload: dict):
    event_id = derive_event_id(payload)  # see below
    if await already_seen(event_id):
        log.info("duplicate event_id=%s — skipping", event_id)
        return
    await mark_seen(event_id)
    await handle(payload)

# 2. Make the downstream write itself idempotent
#    e.g. UPSERT on (conference_uuid, event_name, timestamp)
async def on_conf_end(payload: dict):
    await db.execute(
        "INSERT INTO conference (uuid, ended_at, ...) VALUES (...) "
        "ON CONFLICT (uuid) DO UPDATE SET ended_at = EXCLUDED.ended_at, ..."
    )
```

> ⚠️ **Verify how to derive a stable `event_id`** from your payloads. Candidates: an
> explicit `id`/`uuid` field if present, or a deterministic tuple like
> `(conference_uuid, event, timestamp)` — the right answer depends on your Pexip version's
> payload schema. Document the choice; it's load-bearing.

### Fast ACK, async work

```python
# DO: minimal work in the handler
@app.post("/events")
async def rx(payload: dict = Body(...), _=Depends(check_auth)):
    await durable_append(payload)   # fast, append-only — see below
    return {"status": "ok"}

# DON'T: block the handler on downstream work
@app.post("/events")
async def rx(payload: dict = Body(...), _=Depends(check_auth)):
    await snowflake.insert(transform(payload))  # ❌ multi-second; will time out
    return {"status": "ok"}
```

The pattern is: **durable append → fast ACK → async consumer** for everything that
isn't the cheapest possible write.

### Durable storage — the source of truth

Treat your raw event log as the source of truth. Pexip doesn't expose a replay API; if you
lose events because they went straight to a downstream that broke, they're gone.

| Storage | When to use |
|---|---|
| **Append-only file (JSONL)** | Small deployments, single replica, ops simplicity. Rotate daily. |
| **Local SQLite** | Single replica with query needs. Use WAL mode. |
| **Postgres / MySQL** | Multi-replica receiver, structured downstream queries. |
| **Kafka / Kinesis / Redis Streams** | High volume, multiple downstream consumers, replay. |
| **Cloud object storage** (S3, GCS) | Cold archival; pair with a hot tier for active analytics. |

Whatever you choose, write **before** any non-trivial processing. The durable write is your
insurance against handler bugs, missing event-type routing, and future schema changes.

### Replay & backfill

Because the raw log is durable, you can replay events into a new downstream system:

```python
async def replay(start_ts: float, end_ts: float, handler):
    async for payload in event_log.range(start_ts, end_ts):
        try:
            await handler(payload)
        except Exception:
            log.exception("replay failed payload=%s", payload)
```

This is how you onboard a new BI consumer without re-instrumenting Pexip, fix a bug in an
event handler, or recover from a downstream system outage.

### Scaling the receiver

Event sinks are HTTP — scale horizontally behind a load balancer like any other webhook
receiver. The only constraints:

- **Idempotent handlers** (see above) — without them, a second replica behind the LB will
  produce double-writes.
- **Shared durable store** across replicas. Each replica writes to the same log; no
  per-replica state.
- **Health checks** that reflect real receiver health, not just process liveness. The LB
  should pull a replica with a backed-up queue or a broken DB connection.

Single-replica is fine for low volume. The horizontal-scale story matters when you have
many Conferencing Nodes pushing concurrently or want zero-downtime deploys.

### Dead-letter handling

Some events will always fail (malformed, unknown type, downstream rejects). Don't 5xx them
back to Pexip — you'll just retry forever. Instead:

1. Persist to the main log (always)
2. If a handler raises, **also** persist to a dead-letter store with the failure reason
3. ACK 200 to Pexip
4. Build a tiny ops tool to inspect + manually reprocess the dead-letter store

---

## 5. Common Integrations

| Integration | Shape |
|---|---|
| **Billing / CDR** | `conference_started` + `conference_ended` pairs → conference duration. `participant_connected` + `participant_disconnected` → per-participant minutes. Aggregate nightly. |
| **BI / Analytics** | Append every event to a warehouse (BigQuery, Snowflake, Redshift). Build views on top. |
| **Cold archive** | Compress JSONL by day, push to S3/GCS. Lifecycle-policy to Glacier after N days for compliance/long-term retention. |
| **Real-time dashboard** | Receiver fans out to a WebSocket / SSE layer. UI subscribes per-conference or globally. Keep an in-memory roster derived from connect/disconnect events. |
| **PagerDuty / alerting** | Filter for specific events (e.g. unusual disconnect reasons, conferences ending early) and forward as alerts. |
| **CRM sync** | On `participant_disconnected`, look up the participant's alias in your CRM and log a contact record. |

For most of these, the bulk of the work is the downstream pipeline. The receiver itself is
a thin layer that buys you durability, retry tolerance, and the ability to swap downstream
systems without re-instrumenting Pexip.

---

## 6. Debugging Checklist

### Silent failure modes

| Symptom | Likely cause |
|---|---|
| **No events arriving** | Sink URL/credentials wrong in Pexip admin; sink disabled; firewall blocking; HTTPS cert untrusted. Test connectivity from the Conferencing Node's network. |
| **Events arriving but wrong types missing** | Per-event-type toggle disabled in the sink config; receiver routing not matching the event name (check capitalisation, underscores vs. hyphens). |
| **Receiver gets hammered with duplicates** | Your ACK is slow → Pexip retries → duplicates pile up. Profile the handler; move work async. |
| **Receiver intermittently 502/504 from upstream proxy** | Handler is slow + proxy timeout shorter than handler time. Either speed up the handler (almost always: queue + async) or extend the proxy timeout. |
| **Auth failing** | Basic Auth creds in Pexip sink config don't match what your server expects. Check exact case + special-character escaping. |
| **Out-of-order events** | Don't rely on arrival order. Use the event's own timestamp + `conference_uuid` to reconstruct timeline. |
| **Lost events during deploy** | Receiver downtime overlapped a Pexip emission. Pexip's retries cover only short windows; for HA, run two replicas and stagger deploys. |
| **Schema surprises after Pexip upgrade** | Pexip added/renamed fields in a new version. Your raw-log + durable-store layer makes this recoverable: replay through updated handlers. |

### Testing without Pexip

The simplest sanity check is to POST a representative payload yourself:

```bash
curl -u user:pass -H "Content-Type: application/json" -d @sample_event.json \
  http://localhost:8080/events
```

A representative `conference_started` sample (⚠️ field names approximate; verify against
your version):

```json
{
  "event": "conference_started",
  "version": "1",
  "data": {
    "conference_uuid": "11111111-2222-3333-4444-555555555555",
    "name": "meet.alice",
    "service_type": "conference",
    "service_tag": "alice-vmr",
    "start_time": "2026-05-14T10:00:00Z"
  }
}
```

For each new event type your receiver handles, capture a real payload from your environment
and check it into the repo as a test fixture. Use those fixtures in unit tests for your
handlers — Pexip schema drift is the easiest thing to regress against.

### Built-in tools in Pexip admin

- ⚠️ **Verify**: most Pexip versions offer a **Test event sink** action in admin that POSTs
  a synthetic event to the configured URL — useful for verifying connectivity and auth
  without waiting for a real call.
- **Support log** on the Conferencing Node may show event-sink delivery attempts and
  retry decisions; check there if Pexip-side delivery is in question.

### Always log every receive + every process outcome

```python
log.info("RX event=%s id=%s", event_name, event_id)
# ...
log.info("PROCESSED event=%s id=%s outcome=%s latency_ms=%d",
         event_name, event_id, outcome, latency_ms)
```

The pair `RX` + `PROCESSED` makes it trivial to compute receive rate, processing latency,
and per-event-type error rates from logs alone.

---

## 7. Pre-flight Checklist for a New Event Sink Receiver

- [ ] HTTPS endpoint reachable from every Pexip Conferencing Node (not just one)
- [ ] HTTP Basic Auth credentials configured and validated on every request
- [ ] Endpoint returns `200` within Pexip's per-request timeout (⚠️ verify exact value for your version; budget under 1s)
- [ ] All real processing happens **after** the ACK (queue + async worker pattern)
- [ ] Every event is durably persisted to a raw log **before** any handler runs
- [ ] Idempotency layer in place (dedup by event id, or idempotent downstream writes)
- [ ] Receiver replicas are stateless; durable store is shared
- [ ] Per-event-type handler routing covers every enabled event class (and gracefully no-ops on unknown types — without raising)
- [ ] Dead-letter store for events whose handler raises; ops tool to inspect it
- [ ] Health endpoint reflects real receiver health (queue depth, DB connectivity), not just process liveness
- [ ] Monitoring/alerting on: receive rate, ACK latency p95/p99, error rate, queue depth, dead-letter growth
- [ ] At least one synthetic event-type-per-class fixture under version control; handlers have unit tests against them
- [ ] Tested with `curl` against every event-type code path before connecting Pexip
- [ ] Pexip admin's **Test event sink** action passes against the production URL with production credentials
