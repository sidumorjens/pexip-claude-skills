# Conference Events — Reference

The **conference lifecycle** class of Pexip Infinity event sink events. Fired by a
Conferencing Node when a conference (VMR / gateway call / virtual auditorium / etc.)
starts, changes state, or ends.

> ⚠️ **Verify against your Pexip version.** Field names, casing, and the exact set of
> `*_updated` triggers vary between Infinity releases. The shapes below reflect the
> common pattern; for a binding contract, capture a real payload from your environment
> and check it into your project's test fixtures.

---

## Events in this class

| Event | When it fires |
|---|---|
| `conference_started` | A conference instance begins. For VMRs this is "first participant connects"; for gateway calls, when the call leg is established. |
| `conference_updated` | A conference attribute changes mid-call — typically lock state, name, theme, or similar non-trivial mutation. Not all attribute changes emit an event. |
| `conference_ended` | The conference instance ends. The last participant has left (or the conference was administratively terminated). |

Some Pexip versions also emit additional events in this class (e.g. recording start/stop
treated as conference-level state changes). ⚠️ Verify against your version's docs.

---

## Common envelope

All conference events share an outer envelope and a `data` (or equivalently top-level)
block containing the conference-specific fields:

```json
{
  "event": "conference_started",
  "version": "<schema_version>",
  "data": {
    "conference_uuid": "11111111-2222-3333-4444-555555555555",
    "name": "meet.alice",
    "service_type": "conference",
    "service_tag": "alice-vmr",
    "start_time": "2026-05-14T10:00:00Z"
  }
}
```

> ⚠️ Field placement (top-level vs. nested under `data`) and timestamp format (epoch
> seconds vs. ISO 8601) differ between versions. Write your handler to accept both
> shapes or to coerce on ingest.

---

## Likely fields

The fields below are what you'll typically use to build a CDR or analytics record.
Treat the **names** as approximate; cross-check with a captured sample.

| Field | Type | Notes |
|---|---|---|
| `conference_uuid` | String (UUID) | Stable identifier for this **instance** of the conference. Same VMR called twice produces two `conference_uuid`s. Use this to join `started` → `ended` and to correlate participants. |
| `name` | String | Service name (matches `name` from External Policy `service_configuration`). |
| `service_type` | String | `"conference"`, `"lecture"`, `"gateway"`, `"two_stage_dialing"`, `"media_playback"`, `"test_call"`. |
| `service_tag` | String | Operator-assigned tag, useful for billing groupings. |
| `start_time` | Timestamp | When the conference instance began. |
| `end_time` | Timestamp | (on `conference_ended`) When it ended. |
| `duration` | Number (seconds) | (on `conference_ended`) Convenience field; equivalent to `end_time - start_time`. |
| `instance_id` | String | (some versions) Alternative to or alongside `conference_uuid`. |
| `tag` | String | (some versions) Alternative to `service_tag`. |
| `is_locked` | Boolean | (typically in `*_updated` events) Conference lock state. |
| `participants` | Number | (sometimes in `*_ended`) Total distinct participants seen during the conference. |

> ⚠️ Verify the exact field names — particularly `conference_uuid` vs. `instance_id`,
> and timestamp field naming (`start_time` vs. `start` vs. `started_at`) — against your
> Pexip version's payload.

---

## Worked examples

### `conference_started`

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

Handler shape:

```python
@handler("conference_started")
async def on_conf_start(payload: dict):
    d = payload.get("data", payload)
    await db.execute("""
        INSERT INTO conference (uuid, name, service_type, service_tag, started_at)
        VALUES (:uuid, :name, :stype, :stag, :started_at)
        ON CONFLICT (uuid) DO NOTHING
    """, dict(
        uuid=d["conference_uuid"],
        name=d["name"],
        stype=d.get("service_type"),
        stag=d.get("service_tag"),
        started_at=parse_ts(d["start_time"]),
    ))
```

The `ON CONFLICT … DO NOTHING` makes the insert idempotent — duplicate deliveries (and
manual replays) are harmless.

### `conference_ended`

```json
{
  "event": "conference_ended",
  "version": "1",
  "data": {
    "conference_uuid": "11111111-2222-3333-4444-555555555555",
    "name": "meet.alice",
    "end_time": "2026-05-14T10:43:17Z",
    "duration": 2597
  }
}
```

Handler shape — note this is `UPDATE`, not `INSERT`, because the row was created by
`conference_started`:

```python
@handler("conference_ended")
async def on_conf_end(payload: dict):
    d = payload.get("data", payload)
    await db.execute("""
        UPDATE conference
        SET ended_at = :ended_at, duration_s = :duration
        WHERE uuid = :uuid
    """, dict(
        uuid=d["conference_uuid"],
        ended_at=parse_ts(d["end_time"]),
        duration=d.get("duration"),
    ))
```

### `conference_updated`

```json
{
  "event": "conference_updated",
  "version": "1",
  "data": {
    "conference_uuid": "11111111-2222-3333-4444-555555555555",
    "is_locked": true,
    "timestamp": "2026-05-14T10:12:05Z"
  }
}
```

`conference_updated` carries a subset of conference fields representing what changed.
Treat unknown fields permissively — Pexip may add new ones in future versions.

---

## What if `conference_started` never arrives but `participant_connected` does?

Real systems see this occasionally — usually because the receiver was briefly down when
the conference began. Two reasonable mitigations:

1. **Defensive insert in participant handlers.** When a participant connects, upsert the
   conference row with what you know (uuid, name) so participant rows always have a parent.
2. **Reconciliation pass.** A nightly job that walks the durable event log and rebuilds
   the conference table — catches anything the live handlers missed.

The durable raw-log + idempotent handlers pattern from SKILL.md §4 is what makes both of
these viable.

---

## Common processing patterns

- **CDR row per conference:** one row keyed on `conference_uuid`, populated by
  `started` (insert) → `ended` (update). Aggregate participant minutes from
  `participant-events.md` events into the same row at end-of-day.
- **Real-time roster fan-out:** maintain an in-memory set of active `conference_uuid`s
  for a dashboard. `started` adds; `ended` removes; cleanup on receiver restart by
  rebuilding from `conference` rows where `ended_at IS NULL`.
- **Billing windows:** group conferences by `service_tag` (department / customer / VMR
  owner) and sum `duration` for the billing period. Capture the `service_tag` at
  `started` time — operator changes to the VMR config later shouldn't retroactively
  rewrite finished CDRs.

---

## Test fixture

Capture a real `conference_started` and `conference_ended` from your environment
(use Pexip admin's test-event-sink action or a real test call) and check them into your
project's `tests/fixtures/` directory. Every handler change should run against these
fixtures — Pexip schema drift across versions is the easiest thing to regress on.
