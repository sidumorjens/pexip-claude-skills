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

> **Sourcing:** the payload envelope, event names, and `data` fields below are confirmed
> against two production receivers — one storing to Postgres with a dashboard, one driving
> a real-time conference monitor. The event sink schema in question is **v2**
> (`"version": 2` in the envelope). Pexip's exact retry count + backoff and the
> per-request timeout are still ⚠️ verify-against-your-version — neither receiver measured
> them precisely. For the canonical reference, see
> `https://docs.pexip.com/admin/event_sink.htm`.

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
- **Auth options:** Bearer token (`Authorization: Bearer <secret>`) is the modern, explicit option. Basic Auth is also supported. **IP allowlist** at the receiver is a common defence-in-depth — events come from a small, well-known set of Conferencing Node IPs.
- Pexip discards your response **body** — only the status code matters (typically `200` OK)
- One sink URL receives **all enabled event types**; the event type is in the JSON payload
- **Important:** events are emitted by **Transcoding** Conferencing Nodes only. Proxying Edge Nodes do not emit conference/participant events.

> ⚠️ **Verify** any HMAC payload signing requirement against your Pexip version — neither
> production receiver uses signed payloads, suggesting it's not a standard feature, but
> confirm before relying on its absence in regulated environments.

### Configuration (in Pexip admin)

Configured under **System > Event sinks > Add event sink**. Each sink has:

- **URL** — your endpoint (e.g. `https://receiver.example.com/api/event_sink`)
- **Bearer token** (optional but recommended) — your receiver checks `Authorization: Bearer <token>`
- **Bulk support** toggle — when enabled, Pexip batches multiple events into a single POST as an `eventsink_bulk` envelope. Recommended for high-traffic deployments. (See §4 for unpack pattern.)
- Per-event-class enable toggles
- Verify-connection action that POSTs a synthetic event to test the URL + auth before going live

Multiple sinks can be configured. Every enabled sink receives every enabled event — useful
for separate billing + BI receivers, or for a passive archive alongside a live consumer.

### Delivery semantics

| Property | Behaviour |
|---|---|
| **Delivery** | At-least-once. Duplicates are possible — design for idempotency. |
| **Ordering** | No global ordering. **Per-node ordering** is preserved via the `seq` field (monotonic per Conferencing Node). Across nodes there is no guarantee — correlate by `time` + entity keys (`data.name` for conferences, `data.uuid` for participants), not arrival order. |
| **Retries** | Pexip retries on non-2xx and on timeout. ⚠️ **Verify** exact count + backoff for your version — typical behaviour is a small number of retries with short backoff, then drop. |
| **Timeouts** | ⚠️ **Verify** — Pexip imposes a short per-request timeout (low single-digit seconds). Slow receivers are treated as failures. |
| **Persistence on Pexip side** | None to rely on. If your receiver is down for an extended period, events emitted during the outage may be lost. Build your receiver for HA. |
| **Backpressure** | Pexip will not slow down to match a slow receiver. Either ACK fast and queue, or accept dropped events. |
| **Multi-node delivery** | A conference spanning multiple locations will fire `conference_started` / `_ended` from each Conferencing Node hosting it. Merge by `data.name`; treat the conference as "ended" only when every node has reported `conference_ended`. (See §4.) |

### Common payload envelope

Every event arrives in this envelope (confirmed against v2 receivers):

```json
{
  "node": "10.44.34.11",
  "seq": 688,
  "version": 2,
  "time": 1606392917.976155,
  "event": "participant_disconnected",
  "data": { /* event-specific fields — see references/ */ }
}
```

| Top-level field | Notes |
|---|---|
| `node` | IP address of the Conferencing Node that emitted the event. Use this for per-node `seq` tracking and for multi-node correlation. |
| `seq` | Monotonic sequence number **per node**. Gaps signal missed events; duplicates of the same `(node, seq)` are retries. The natural idempotency key — see §4. |
| `version` | Schema version. Current is `2`. Major bumps signal breaking changes to `data`. |
| `time` | Epoch seconds as a float (e.g. `1606392917.976155`). Pexip's perspective on when the event happened — prefer this over your `received_at` for analytics. |
| `event` | The event type name (e.g. `conference_started`). See §2. |
| `data` | Event-specific payload. Shape depends on `event` — see `references/`. For `eventsink_bulk`, `data` is a **list** of single-event envelopes (see §4). |

### Bulk mode

When **Bulk support** is enabled on the sink, Pexip batches events into a single POST:

```json
{
  "node": "127.0.0.1",
  "seq": 0,
  "event": "eventsink_bulk",
  "data": [
    { "node": "10.44.34.14", "seq": 2183, "event": "participant_connected", "data": { ... } },
    { "node": "10.44.34.14", "seq": 2184, "event": "participant_updated",  "data": { ... } }
  ]
}
```

Your receiver must detect `event == "eventsink_bulk"` and dispatch each inner element
through the same handler as single events. The pattern is in §4.

### A note on what's pushed vs. polled

Event sinks push **lifecycle events**. They are **not**:

- A live participant roster (use the Management API `status/v1/participant/`)
- A real-time media-quality stream (that's a separate feed)
- A way to control calls (use the Management API for mid-call actions)

If your use case needs real-time control, combine event sinks (for state changes) with
Management API calls (for actions you want to take in response).

---

## 2. Event Types

Pexip v2 event sinks emit the following event classes. The two with reference files in
this skill — conference and participant lifecycle — are where most integrations live.

| Class | Events | Reference |
|---|---|---|
| **Conference lifecycle** | `conference_started`, `conference_updated`, `conference_ended` | `references/conference-events.md` |
| **Participant lifecycle** | `participant_connected`, `participant_updated`, `participant_disconnected` | `references/participant-events.md` |
| **Participant media quality** | `participant_media_stream_window` (mid-call quality change), `participant_media_streams_destroyed` (end-of-call media stats) | (No dedicated reference yet — see notes below.) |
| **Sink lifecycle** | `eventsink_started`, `eventsink_updated`, `eventsink_stopped` — emitted when the sink itself is enabled / modified / disabled on a Conferencing Node. Useful for receiver-side observability. | — |
| **Bulk wrapper** | `eventsink_bulk` — wraps multiple events in one POST. See §1 and §4. | — |

### Media quality events (brief)

`participant_media_stream_window` arrives mid-call when Pexip's quality estimator changes
classification. Useful for live dashboards. The relevant `data` fields seen in production:

- `uuid` — the participant
- `call_quality_now` — string from the set `"0_unknown"`, `"1_good"`, `"2_ok"`, `"3_bad"`, `"4_terrible"`
- Window timing fields (start/end of the measurement window)

`participant_media_streams_destroyed` fires at end-of-call with cumulative media stats.
Most receivers log it for analytics; few drive logic from it.

> ⚠️ Other event classes (presentation, recording, transcript, alarms) may exist in your
> Pexip version depending on licensing and feature toggles. Check the official docs for
> the full list. Reference files for these can be added to this skill as needed.

### Correlating events into a call record

A typical CDR or analytics row is built by joining:

- One `conference_started` and one `conference_ended` per conference, matched on **`data.name`** — Pexip's documented correlation key, stable across the conference's lifetime and across multiple Conferencing Nodes hosting the same conference.
- N `participant_connected` and N `participant_disconnected` per conference, matched on **`data.uuid`** (participant) and **`data.conference`** (parent conference name).
- Optional `*_updated` events for state changes mid-call (role change, lock change, mute change, etc.).

Two things to keep front-of-mind when correlating:

1. **Conference identity is the `name`, not a UUID.** Same `name` can appear from multiple `node` IPs during a single conference; merge them.
2. **Participant identity is the `uuid`.** The participant's `data.conference` field tells you which conference (by name) the participant is in.

The receiver pattern in §4 (durable append-only log + idempotency by `(node, seq)` +
downstream aggregation) makes this correlation robust against duplicate delivery,
out-of-order arrival, and per-node restart loops.

---

## 3. Implementing a Receiver

### Minimal FastAPI skeleton

The key principle: **ACK fast, process asynchronously**. Returning `200 OK` quickly stops
Pexip retrying; the actual work happens off the request thread. The receiver below uses
the recommended Bearer token auth, handles both single events and `eventsink_bulk`, and
routes by event name through a small registry.

```python
import asyncio
import logging
import os

from fastapi import FastAPI, Header, HTTPException, Request, Response

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("event-sink")

EVENT_SINK_TOKEN = os.environ.get("EVENT_SINK_TOKEN")  # optional Bearer secret
ALLOWED_SOURCES  = [s.strip() for s in os.getenv("ALLOWED_SINK_SOURCES", "").split(",") if s.strip()]

app = FastAPI()

# Off-thread processing queue (swap for Redis/SQS/Kafka in production — see §4)
event_queue: asyncio.Queue = asyncio.Queue(maxsize=10_000)


def _check_auth(request: Request, authorization: str | None) -> None:
    """Bearer token if configured; else allow trusted IPs (defence-in-depth)."""
    if EVENT_SINK_TOKEN:
        expected = f"Bearer {EVENT_SINK_TOKEN}"
        if authorization != expected:
            raise HTTPException(status_code=401, detail="invalid token")
        return
    # No token configured — fall back to IP allowlist if you've set one.
    if ALLOWED_SOURCES:
        from ipaddress import ip_address, ip_network
        ip = ip_address(request.client.host)
        if not any(ip in ip_network(n, strict=False) for n in ALLOWED_SOURCES):
            raise HTTPException(status_code=401, detail="source not allowed")


@app.post("/api/event_sink")
async def receive_event(
    request: Request,
    authorization: str | None = Header(default=None),
):
    _check_auth(request, authorization)

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid JSON")

    # Pull the envelope fields for logging + dispatch
    event = payload.get("event", "<unknown>")
    node  = payload.get("node")
    seq   = payload.get("seq")
    log.info("RX event=%s node=%s seq=%s", event, node, seq)

    # ACK immediately; defer real processing
    try:
        event_queue.put_nowait(payload)
    except asyncio.QueueFull:
        # Don't 5xx — Pexip will retry and pile up duplicates.
        # ACK and log loudly that we're shedding load; alarm on queue depth.
        log.error("event_queue FULL — dropping event=%s node=%s seq=%s", event, node, seq)

    return Response(status_code=200)


@app.get("/api/event_sink/status")
async def sink_status():
    return {"queue_depth": event_queue.qsize()}


@app.get("/healthz")
async def healthz():
    return {"ok": True}


@app.on_event("startup")
async def _start_worker():
    asyncio.create_task(_worker())


async def _worker():
    while True:
        envelope = await event_queue.get()
        try:
            await dispatch(envelope)
        except Exception:
            log.exception("processing failed event=%s", envelope.get("event"))
        finally:
            event_queue.task_done()


# ── Per-event-type routing ────────────────────────────────────────────────────

HANDLERS = {}

def handler(event_name: str):
    def deco(fn):
        HANDLERS[event_name] = fn
        return fn
    return deco


async def dispatch(envelope: dict) -> None:
    """
    Handles both single events and eventsink_bulk wrappers.
    Pass each inner element through the registry; persist-before-dispatch is
    the caller's responsibility (see §4).
    """
    event = envelope.get("event", "")

    # Bulk wrapper — unpack and dispatch each inner event
    if event == "eventsink_bulk":
        inner_list = envelope.get("data") or []
        if not isinstance(inner_list, list):
            log.warning("eventsink_bulk with non-list data")
            return
        log.info("bulk envelope: %d inner events", len(inner_list))
        for inner in inner_list:
            await dispatch(inner)
        return

    fn = HANDLERS.get(event)
    if fn is None:
        log.debug("no handler for event=%s — payload kept in durable log only", event)
        return
    await fn(envelope)


@handler("conference_started")
async def on_conf_start(envelope: dict):
    data = envelope.get("data", {})
    # See references/conference-events.md for the full field shape
    ...

@handler("participant_connected")
async def on_p_connect(envelope: dict):
    data = envelope.get("data", {})
    # See references/participant-events.md for the full field shape
    ...
```

Notes:

- **One endpoint receives all event types.** Route by `envelope["event"]` inside the dispatcher.
- **Endpoint URL is your choice.** Both `/api/event_sink` (underscore) and `/event-sink` (hyphen) are conventions seen in production — whichever you pick, just configure it in Pexip's Event Sink settings.
- **Return 200 even on queue-full.** Pexip retrying a flood you can't store is worse than dropping it — alarm on queue depth instead.
- **Defer all I/O** (DB writes, downstream HTTP calls) into the worker. The request handler must not block.
- **Always persist before dispatch.** If a handler is missing or fails, the raw envelope must still be in your durable log so you can replay it once the handler exists. The skeleton above leaves persistence to `§4`-style patterns — wire it into `dispatch()` or do an `await durable_append(envelope)` immediately after the auth check.

### Docker Compose pattern

```yaml
services:
  event-sink:
    build: .
    environment:
      - EVENT_SINK_TOKEN=change-me
      - ALLOWED_SINK_SOURCES=10.0.0.0/8,192.168.0.0/16
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

The natural idempotency key is **`(node, seq)`** from the envelope. `seq` is monotonic
per Conferencing Node and resets only when the sink restarts on that node — combining it
with `node` gives you a globally-unique-enough identifier with no derivation needed.

```python
# Dedup at ingest by (node, seq)
async def process(envelope: dict):
    node = envelope.get("node") or "unknown"
    seq  = envelope.get("seq")
    if seq is None:
        # Bulk wrapper or older payload — fall through to the downstream-write
        # idempotency below.
        await handle(envelope)
        return
    if await already_seen(node, seq):
        log.info("duplicate (node=%s, seq=%s) — skipping", node, seq)
        return
    await mark_seen(node, seq)  # store with a TTL of e.g. 24h
    await handle(envelope)
```

In addition (or instead), make the downstream write itself idempotent. Belt-and-braces is
cheap:

```python
# UPSERT keyed on the entity identifier from the data block
async def on_conf_end(envelope: dict):
    d = envelope["data"]
    await db.execute("""
        INSERT INTO conference (name, ended_at, end_time)
        VALUES (:name, NOW(), :end_time)
        ON CONFLICT (name) DO UPDATE
           SET ended_at = EXCLUDED.ended_at,
               end_time = EXCLUDED.end_time
    """, dict(name=d["name"], end_time=d.get("end_time")))
```

### Multi-node delivery — merge conferences by `data.name`

A conference spanning multiple Conferencing Node locations will fire `conference_started`
and `conference_ended` from **each node** hosting it. The recommended pattern from Pexip
(and the one used by production receivers) is:

1. Conference identity = `data.name`. Same name from different `node` IPs = same conference.
2. Track an `active_nodes: set[str]` per conference. Add on `conference_started`, discard on `conference_ended`.
3. Treat the conference as **ended** only when `active_nodes` is empty.
4. On `conference_started` from a new node, merge — update `start_time` to the **earliest** value seen.

```python
async def conference_started(data: dict, node: str):
    conf = store.get(data["name"])
    if conf is None:
        store[data["name"]] = Conference(
            name=data["name"],
            start_time=data.get("start_time"),
            active_nodes={node},
            ...
        )
    else:
        conf.active_nodes.add(node)
        new_start = data.get("start_time")
        if new_start and (not conf.start_time or new_start < conf.start_time):
            conf.start_time = new_start

async def conference_ended(data: dict, node: str):
    conf = store.get(data["name"])
    if not conf:
        return
    conf.active_nodes.discard(node)
    if not conf.active_nodes:
        conf.end_time = data.get("end_time")
        store.pop(data["name"])
```

Without this pattern, a multi-node conference appears to "end" the moment the first node
finishes its share — losing data about the participants still on other nodes.

### Bulk mode — unpack before dispatch

When the **Bulk support** toggle is enabled on the sink, Pexip wraps multiple events in a
single POST as `event: "eventsink_bulk"` with `data` as an **array** of single-event
envelopes. Dispatch each inner envelope individually:

```python
async def dispatch(envelope: dict):
    if envelope.get("event") == "eventsink_bulk":
        for inner in envelope.get("data", []):
            await dispatch(inner)   # recurse for safety
        return
    # ... handle single event as normal
```

Each inner envelope has its own `node`, `seq`, `time`, `event`, `data` — treat it
identically to a non-bulk event for idempotency, persistence, and routing.

### Persist-before-dispatch — the survival pattern for unknown events

When Pexip ships a new event type in a future version, your routed handlers will silently
skip it. If you persisted only after dispatch, that event is **lost**. Always:

```python
async def receive(envelope: dict):
    await durable_append(envelope)     # 1. always persist the raw envelope
    await dispatch(envelope)           # 2. then dispatch via the registry
```

This is what makes replay (below) viable when you later add a handler for the new type.

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
| **No events arriving** | Sink URL/token wrong in Pexip admin; sink disabled; firewall blocking; HTTPS cert untrusted. Test connectivity from the Conferencing Node's network. Use Pexip admin's verify-connection action on the sink. |
| **Events arriving but wrong types missing** | Per-event-class toggle disabled in the sink config; receiver routing not matching the event name (check exact spelling — `conference_ended` is the v2 name; old `conference_end` may appear from legacy configs). |
| **Many `seq` gaps from one node** | Receiver returned 5xx during a burst and Pexip dropped events after exhausting retries; or a CN restarted (seq resets on sink restart per node — gap is expected once). Alarm on sustained gaps, not single ones. |
| **Receiver gets hammered with duplicates** | Your ACK is slow → Pexip retries → duplicates pile up. Profile the handler; ensure all real work is off the request thread. Check that `(node, seq)` dedup is in place. |
| **Receiver intermittently 502/504 from upstream proxy** | Handler is slow + proxy timeout shorter than handler time. Either speed up the handler (almost always: queue + async) or extend the proxy timeout. |
| **Auth failing** | Bearer token in Pexip sink config doesn't match what your server expects. Check exact value, no trailing whitespace, no implicit URL-encoding. |
| **Conferences appear to end too early** | Multi-node conference and your store removes on the first `conference_ended` instead of waiting for `active_nodes` to drain. Use the merge pattern in §4. |
| **Conferences "linger" after they should have ended** | Reverse: some `conference_ended` events from one or more nodes never arrived (receiver was down during their emission). Add a stale-conference reaper (e.g. drop after 2h with no events). |
| **Sink "receiving" indicator flaps** | Pattern: declare the sink stale if no event in the last ~2 minutes. Low-activity deployments may legitimately go quiet; tune the threshold to your traffic profile. |
| **Bulk mode events not dispatched** | Receiver doesn't detect `event == "eventsink_bulk"` and unpack `data` as a list — single events arrive fine, then mysterious gaps when traffic spikes and Pexip switches to batching. |
| **Out-of-order events across nodes** | No global ordering. Use `time` (epoch float) + entity keys to reconstruct timeline. Per-node ordering is preserved via `seq`. |
| **Lost events during deploy** | Receiver downtime overlapped Pexip emissions. Pexip's retries cover only short windows; for HA, run two replicas, stagger deploys, share the durable store. |
| **Schema surprises after Pexip upgrade** | New fields added or renamed in a new version. Persist-before-dispatch + raw-log layer makes this recoverable: replay through updated handlers. |
| **Host appears in every breakout room** | Hosts monitoring breakouts show up as participants in all of them, but only one has `has_media: true`. Filter on `has_media` for "actually present" rosters. |

### Testing without Pexip

POST a representative payload yourself:

```bash
TOKEN="change-me"
curl -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d @sample_conference_started.json \
     http://localhost:8080/api/event_sink
```

A representative v2 `conference_started` envelope (use this shape verbatim — confirmed
against production receivers):

```json
{
  "node": "10.44.34.11",
  "seq": 1,
  "version": 2,
  "time": 1747218000.123,
  "event": "conference_started",
  "data": {
    "name": "meet.alice",
    "service_type": "conference",
    "tag": "alice-vmr",
    "start_time": 1747218000.0,
    "is_locked": false,
    "is_started": true,
    "guests_muted": false
  }
}
```

A representative `eventsink_bulk` wrapping two inner events:

```json
{
  "node": "10.44.34.11",
  "seq": 0,
  "event": "eventsink_bulk",
  "data": [
    { "node": "10.44.34.11", "seq": 2, "version": 2, "time": 1747218005.1,
      "event": "participant_connected",
      "data": { "uuid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                "conference": "meet.alice", "display_name": "Alice",
                "role": "chair", "protocol": "webrtc",
                "connect_time": 1747218005.0, "has_media": true } },
    { "node": "10.44.34.11", "seq": 3, "version": 2, "time": 1747218010.2,
      "event": "participant_updated",
      "data": { "uuid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                "conference": "meet.alice", "is_presenting": true } }
  ]
}
```

For each new event type your receiver handles, capture a real payload from your
environment and check it into the repo as a test fixture. Use those fixtures in unit
tests — schema drift across Pexip versions is the easiest thing to regress against.

### Built-in tools in Pexip admin

- **Verify-connection action** on each sink in **System > Event sinks** — POSTs a synthetic event to test connectivity + auth + parsing without waiting for a real call.
- **Support log** on the Conferencing Node may show event-sink delivery attempts and retry decisions; check there if Pexip-side delivery is in question.

### Always log every receive + every process outcome

```python
log.info("RX event=%s node=%s seq=%s", event, node, seq)
# ...
log.info("PROCESSED event=%s node=%s seq=%s outcome=%s latency_ms=%d",
         event, node, seq, outcome, latency_ms)
```

The pair `RX` + `PROCESSED` keyed on `(node, seq)` makes it trivial to compute receive
rate, processing latency, per-node throughput, and per-event-type error rates from logs
alone — and to spot dedup hits when the same `(node, seq)` shows up twice.

---

## 7. Pre-flight Checklist for a New Event Sink Receiver

- [ ] HTTPS endpoint reachable from **every** Transcoding Conferencing Node (not just one — Proxying Edge Nodes don't emit, but every transcoding node does)
- [ ] Bearer token validated on every request (or IP allowlist if you've chosen token-less + trusted-network)
- [ ] Endpoint returns `200` within Pexip's per-request timeout (⚠️ verify exact value for your version; budget under 1s)
- [ ] All real processing happens **after** the ACK (queue + async worker pattern)
- [ ] Every envelope is durably persisted to a raw log **before** any handler runs
- [ ] Idempotency by `(node, seq)` in place (or idempotent downstream UPSERTs as belt-and-braces)
- [ ] **Bulk dispatch** implemented — receiver detects `event == "eventsink_bulk"` and unpacks the inner list. Tested with a synthetic bulk fixture.
- [ ] **Multi-node merge** for conferences — same `data.name` from multiple `node` IPs merges to one logical conference; `conference_ended` only fully ends when `active_nodes` is empty.
- [ ] Receiver replicas are stateless; durable store is shared
- [ ] Per-event handler routing covers every enabled event (and gracefully no-ops on unknown types — without raising)
- [ ] Dead-letter store for events whose handler raises; ops tool to inspect it
- [ ] Health endpoint reflects real receiver health (queue depth, DB connectivity, last-event-time staleness), not just process liveness
- [ ] Stale-sink detection — alarm if no events for N minutes (typical: 2 minutes for active deployments)
- [ ] Monitoring/alerting on: receive rate, ACK latency p95/p99, error rate, queue depth, dead-letter growth, per-node `seq` gaps
- [ ] At least one synthetic fixture per event class under version control; handlers have unit tests against them
- [ ] Tested with `curl` against every event-type code path before connecting Pexip
- [ ] Pexip admin's **verify-connection** action passes against the production URL with production token
