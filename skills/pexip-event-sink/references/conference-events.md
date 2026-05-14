# Conference Events — Reference

The **conference lifecycle** class of Pexip Infinity event sink events. Fired by a
Transcoding Conferencing Node when a conference (VMR / gateway call / virtual auditorium /
etc.) starts, changes state, or ends.

> **Sourcing:** field set below is taken from two production receivers running against
> v2 event sinks (`"version": 2` in the envelope). Field names match what real
> Conferencing Nodes emit. Older v1 deployments may differ in field placement; envelope
> top-level fields (`node`, `seq`, `version`, `time`, `event`, `data`) and the
> `data.name` correlation key are stable.

---

## Events in this class

| Event | When it fires |
|---|---|
| `conference_started` | A conference instance begins on a Conferencing Node. For multi-node conferences, fires once per node hosting it. |
| `conference_updated` | A conference attribute changes mid-call — lock state, started flag, guest-mute state. |
| `conference_ended` | The conference instance ends on a Conferencing Node. For multi-node conferences, fires once per node — the conference is only **really** ended when every node has reported. |

---

## Envelope

Every event arrives in the same v2 envelope:

```json
{
  "node": "10.44.34.11",
  "seq": 688,
  "version": 2,
  "time": 1606392917.976155,
  "event": "conference_started",
  "data": { /* conference-specific fields below */ }
}
```

See SKILL.md §1 for the envelope semantics. Use `data.name` (not `node`, not anything in
the envelope) as the conference correlation key.

---

## `data` fields

| Field | Type | Notes |
|---|---|---|
| `name` | String | **The correlation key.** Pexip's own guidance: "This can be used to correlate conference events for the same conference across multiple Conferencing Nodes." Same `name` from different `node` IPs = same logical conference. |
| `service_type` | String (enum) | One of: `connecting`, `conference`, `gateway`, `lecture`, `test_call`, `waiting_room`, `two_stage_dialing`, `media_playback`, `ivr`. Default conference type if unknown is safe (`"conference"`). |
| `tag` | String | Operator-assigned service tag. Useful for billing groupings. May be absent or empty — coalesce to `NULL` rather than `""`. |
| `start_time` | Float (epoch seconds) | When the conference began **on this node**. For multi-node conferences, merge to the **earliest** value across all `conference_started` events for the same `name`. |
| `end_time` | Float (epoch seconds) | (on `conference_ended`) When it ended on this node. |
| `is_locked` | Boolean | Lock state. Appears in `started` and in `updated` when changed. |
| `is_started` | Boolean | Whether the conference has actually started (transitioned past "waiting for host"). |
| `guests_muted` | Boolean | Whether guests are muted by host action. |

> ⚠️ Other fields (e.g. recording state, IVR theme name) may appear in your deployment
> depending on licensing. Persist the full raw envelope (§4) so you don't lose data you
> haven't yet wired into your handler.

---

## Worked examples

### `conference_started`

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

Handler shape — note the multi-node merge (insert-then-add-node, no-op if already known):

```python
@handler("conference_started")
async def on_conf_start(envelope: dict):
    d = envelope["data"]
    node = envelope.get("node", "")
    async with store_lock:
        conf = store.get(d["name"])
        if conf is None:
            store[d["name"]] = Conference(
                name=d["name"],
                service_type=d.get("service_type", "conference"),
                tag=d.get("tag") or None,
                start_time=d.get("start_time"),
                is_locked=d.get("is_locked", False),
                is_started=d.get("is_started", False),
                guests_muted=d.get("guests_muted", False),
                active_nodes={node},
            )
        else:
            conf.active_nodes.add(node)
            new_start = d.get("start_time")
            if new_start and (not conf.start_time or new_start < conf.start_time):
                conf.start_time = new_start
```

### `conference_updated`

`conference_updated` carries **only the fields that changed**. Treat unknown fields
permissively and apply as a partial update:

```json
{
  "node": "10.44.34.11",
  "seq": 47,
  "version": 2,
  "time": 1747218600.5,
  "event": "conference_updated",
  "data": {
    "name": "meet.alice",
    "is_locked": true
  }
}
```

```python
@handler("conference_updated")
async def on_conf_update(envelope: dict):
    d = envelope["data"]
    conf = store.get(d["name"])
    if not conf:
        return
    for key in ("is_locked", "is_started", "guests_muted", "tag"):
        if key in d:
            setattr(conf, key, d[key])
```

### `conference_ended`

```json
{
  "node": "10.44.34.11",
  "seq": 320,
  "version": 2,
  "time": 1747220597.1,
  "event": "conference_ended",
  "data": {
    "name": "meet.alice",
    "end_time": 1747220597.0
  }
}
```

Multi-node teardown — only fully end when every node has reported:

```python
@handler("conference_ended")
async def on_conf_end(envelope: dict):
    d = envelope["data"]
    node = envelope.get("node", "")
    async with store_lock:
        conf = store.get(d["name"])
        if not conf:
            return
        conf.active_nodes.discard(node)
        if not conf.active_nodes:
            conf.end_time = d.get("end_time")
            store.pop(d["name"])
            await persist_cdr(conf)   # final write to your CDR table
```

---

## Service types

The `service_type` field on `conference_started` is one of:

| Value | Meaning |
|---|---|
| `conference` | Standard VMR. |
| `lecture` | Virtual Auditorium (Host/Guest with separate views). |
| `gateway` | Infinity Gateway call (incoming → outgoing protocol transform). |
| `two_stage_dialing` | Virtual Reception (IVR with DTMF entry). |
| `media_playback` | Media Playback Service. |
| `test_call` | Test Call Service. |
| `connecting` | Transitional state — a participant is mid-connection. |
| `waiting_room` | Participant is in a waiting room. |
| `ivr` | An IVR flow. |

For analytics, the meaningful long-running types are `conference`, `lecture`, and
`gateway`. The others are typically short-lived states you can group as "transitional".

---

## Breakout rooms

Breakout rooms appear as conferences whose `name` matches the pattern:

```
{parent_name}_breakout_{uuid}
```

For example: `"Dennis test_breakout_4ce6aa27-e550-4e02-be1f-90b3b15a2eaf"` is a breakout
of the parent conference `"Dennis test"`. Detect with a regex:

```python
import re

_BREAKOUT_PATTERN = re.compile(r'^(.+?)_breakout_([0-9a-f\-]+)$', re.IGNORECASE)

def parse_breakout_name(conf_name: str) -> tuple[str | None, str | None]:
    m = _BREAKOUT_PATTERN.match(conf_name)
    if m:
        return m.group(1), m.group(2)
    return None, None
```

Operational notes for breakouts:

- A breakout can start **before** the host joins the main VMR. Be prepared to auto-create the parent conference when you first see a breakout for a parent you don't yet have a record of.
- Breakouts emit the same `conference_started` / `_ended` events as any other conference; nothing special on the wire.
- For roster/dashboard purposes, group breakouts under their parent rather than as top-level conferences — see SKILL.md §5.

---

## What if `conference_started` never arrives but `participant_connected` does?

Real systems see this occasionally — usually because the receiver was briefly down when
the conference began. Two mitigations the production receivers use:

1. **Auto-create from participant.** When a participant connects to a conference name the store doesn't know about, create the conference row from what the participant event tells you (`conference` name, derived service_type).
2. **Reconciliation pass.** A periodic job that walks the durable event log and rebuilds the conference table — catches anything the live handlers missed.

The durable raw-log + idempotent handlers pattern from SKILL.md §4 is what makes both
viable. Combined with the `(node, seq)` dedup, both are safe to run repeatedly.

---

## Common processing patterns

- **CDR row per conference:** keyed on `name`, populated by `conference_started` (insert), updated by `conference_ended` (final fields). Aggregate participant minutes from `participant-events.md` events into the same row at end-of-day.
- **Real-time roster fan-out:** keep an in-memory `{name: Conference}` for a dashboard. WebSocket / SSE push on `_started` / `_updated` / `_ended`. Cold-start by querying `conference` rows where `ended_at IS NULL`.
- **Billing windows:** group conferences by `tag` (department / customer / VMR owner) and sum duration for the billing period. Capture `tag` at `started` time — operator changes to the VMR config later shouldn't retroactively rewrite finished CDRs.
- **Service-type filtering:** for billing, typically exclude `test_call`, `connecting`, `waiting_room`, `ivr` — they're transitional and not chargeable.

---

## Test fixture

Capture a real `conference_started` and `conference_ended` pair from your environment
(use Pexip admin's verify-connection action on the sink, or a real test call). Check both
single-event and `eventsink_bulk` shapes into your `tests/fixtures/` directory. Every
handler change should run against these fixtures.
