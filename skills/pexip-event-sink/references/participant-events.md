# Participant Events — Reference

The **participant lifecycle** class of Pexip Infinity event sink events. Fired by a
Conferencing Node when a participant joins a conference, changes state mid-call, or
disconnects.

> ⚠️ **Verify against your Pexip version.** Field names, the granularity of
> `participant_updated` triggers, and disconnect-reason vocabulary vary between Infinity
> releases. The shapes below reflect the common pattern; capture a real payload from
> your environment and check it into your project's test fixtures.

---

## Events in this class

| Event | When it fires |
|---|---|
| `participant_connected` | A participant has joined a conference. For WebRTC + SSO, this is after authentication; for SIP/H.323, after any PIN entry. |
| `participant_updated` | A participant's attributes change — role (chair↔guest), display name override, layout group, mute state, etc. Not all attribute changes emit an event. |
| `participant_disconnected` | A participant has left the conference. Includes a disconnect reason. |

---

## Common envelope

```json
{
  "event": "participant_connected",
  "version": "<schema_version>",
  "data": {
    "participant_uuid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "conference_uuid": "11111111-2222-3333-4444-555555555555",
    "display_name": "Alice",
    "remote_alias": "sip:alice@example.com",
    "remote_address": "10.20.30.40",
    "protocol": "sip",
    "role": "chair",
    "connect_time": "2026-05-14T10:00:05Z"
  }
}
```

> ⚠️ Field placement (top-level vs. nested under `data`) and timestamp format vary
> between versions. Write handlers to accept both shapes or coerce on ingest.

---

## Likely fields

| Field | Type | Notes |
|---|---|---|
| `participant_uuid` | String (UUID) | Stable identifier for this participant's session in this conference. Use this to join `connected` → `disconnected`. |
| `call_uuid` | String (UUID) | A call-leg identifier. For WebRTC two-stage joins (`api` then `standard`), the two stages may share a `call_uuid` but have different `participant_uuid`s. ⚠️ Verify against your version. |
| `conference_uuid` | String (UUID) | The conference this participant is in. Same as in `conference-events.md`. Use this to join into a CDR. |
| `display_name` | String | Display name shown in the conference. May have been overridden by External Policy. |
| `remote_alias` | String | The alias the participant dialed in as. May include scheme (`sip:`, `h323:`, etc.). |
| `remote_address` | String | IP address of the participant's endpoint. |
| `protocol` | String | `"webrtc"`, `"sip"`, `"h323"`, `"rtmp"`, `"teams"`, `"mssip"`, `"api"`. |
| `role` | String | `"chair"` / `"guest"`. May be `null` at certain pre-auth stages. |
| `connect_time` | Timestamp | When the participant joined. |
| `disconnect_time` | Timestamp | (on `disconnected`) When the participant left. |
| `duration` | Number (seconds) | (on `disconnected`) Convenience field for `disconnect_time - connect_time`. |
| `disconnect_reason` | String | (on `disconnected`) See below. |
| `is_streaming` | Boolean | Whether the participant is a streaming/recording endpoint rather than a human. Useful for filtering them out of attendance counts. |
| `is_presenting` | Boolean | Whether the participant is currently sending presentation content. May appear in `*_updated` events. |
| `service_tag` | String | Inherited from the conference; sometimes present on participant events for easier billing aggregation. |
| `bandwidth` | Number | Current call bandwidth (bps). |
| `vendor` | String | Endpoint vendor/version string. |

> ⚠️ Verify the exact field names — particularly `participant_uuid` vs. `uuid` and
> `connect_time` vs. `connected_at` — against your Pexip version's payload.

---

## `disconnect_reason` vocabulary

⚠️ The exact set of values is version-specific. Commonly seen values include:

| Reason | Meaning |
|---|---|
| `"User initiated"` / `"hangup"` | Participant ended the call. |
| `"Owner initiated"` | A host/admin disconnected them via the Management API or the in-conference controls. |
| `"Conference ended"` | The whole conference ended while they were still in it. |
| `"No host"` / `"Waiting for host expired"` | Guests-waiting-for-host timed out. |
| `"PIN entry failed"` / `"Authentication failed"` | Couldn't pass entry checks. |
| `"Conference full"` | Hit the conference participant limit. |
| `"Media error"` / `"Network error"` | Media-layer failure. |
| `"Timeout"` | Generic timeout. |

Build your handlers to handle unknown reasons gracefully (log + treat as
`"Unknown"`) — Pexip versions add new reasons over time.

---

## Worked examples

### `participant_connected`

```json
{
  "event": "participant_connected",
  "version": "1",
  "data": {
    "participant_uuid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "conference_uuid": "11111111-2222-3333-4444-555555555555",
    "display_name": "Alice",
    "remote_alias": "sip:alice@example.com",
    "remote_address": "10.20.30.40",
    "protocol": "sip",
    "role": "chair",
    "connect_time": "2026-05-14T10:00:05Z",
    "is_streaming": false
  }
}
```

Handler:

```python
@handler("participant_connected")
async def on_p_connect(payload: dict):
    d = payload.get("data", payload)
    await db.execute("""
        INSERT INTO participant
            (uuid, conference_uuid, display_name, remote_alias, remote_address,
             protocol, role, connected_at, is_streaming)
        VALUES
            (:uuid, :conf, :dname, :alias, :addr, :proto, :role, :connected_at, :streaming)
        ON CONFLICT (uuid) DO NOTHING
    """, dict(
        uuid=d["participant_uuid"],
        conf=d["conference_uuid"],
        dname=d.get("display_name"),
        alias=d.get("remote_alias"),
        addr=d.get("remote_address"),
        proto=d.get("protocol"),
        role=d.get("role"),
        connected_at=parse_ts(d["connect_time"]),
        streaming=d.get("is_streaming", False),
    ))
```

### `participant_disconnected`

```json
{
  "event": "participant_disconnected",
  "version": "1",
  "data": {
    "participant_uuid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "conference_uuid": "11111111-2222-3333-4444-555555555555",
    "disconnect_time": "2026-05-14T10:32:14Z",
    "duration": 1929,
    "disconnect_reason": "User initiated"
  }
}
```

Handler:

```python
@handler("participant_disconnected")
async def on_p_disconnect(payload: dict):
    d = payload.get("data", payload)
    await db.execute("""
        UPDATE participant
        SET disconnected_at = :dt, duration_s = :dur, disconnect_reason = :reason
        WHERE uuid = :uuid
    """, dict(
        uuid=d["participant_uuid"],
        dt=parse_ts(d["disconnect_time"]),
        dur=d.get("duration"),
        reason=d.get("disconnect_reason"),
    ))
```

### `participant_updated`

```json
{
  "event": "participant_updated",
  "version": "1",
  "data": {
    "participant_uuid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "conference_uuid": "11111111-2222-3333-4444-555555555555",
    "role": "guest",
    "timestamp": "2026-05-14T10:05:30Z"
  }
}
```

`participant_updated` carries only the changed fields. Apply as a partial update; don't
assume omitted fields have changed to `null`.

```python
@handler("participant_updated")
async def on_p_update(payload: dict):
    d = payload.get("data", payload)
    changes = {k: v for k, v in d.items()
               if k in {"display_name", "role", "is_presenting", "is_streaming"}}
    if not changes:
        return
    cols = ", ".join(f"{k} = :{k}" for k in changes)
    await db.execute(
        f"UPDATE participant SET {cols} WHERE uuid = :uuid",
        {**changes, "uuid": d["participant_uuid"]},
    )
```

---

## WebRTC two-stage joins

For Pexip's WebRTC apps, a single user join may produce **two** `participant_connected`
events in quick succession — first with `protocol: "api"` (or `participant_type: "api"`),
then with `protocol: "webrtc"` (or `participant_type: "standard"`). Decide whether your
analytics/billing should:

- Count both (rare — usually inflates the participant count)
- Count only the `standard` / non-`api` join (typical for human-participant analytics)
- Count only the first connect per `call_uuid` (if available)

The right policy depends on the consumer. Document the choice in the handler.

> ⚠️ Verify the exact field name (`participant_type` vs. `protocol` value) for the
> two-stage signal in your Pexip version. This is the same two-stage pattern the
> `pexip-external-policy` skill mentions for participant policy.

---

## Common processing patterns

- **Attendance row per participant:** one row per `participant_uuid`, inserted on
  `connected`, updated on `disconnected`. Join to the `conference` table on
  `conference_uuid`.
- **Real-time roster:** maintain an in-memory `{conference_uuid: set[participant_uuid]}`
  for a live dashboard. Add on `connected`, remove on `disconnected`. Cold-start by
  querying for rows where `disconnected_at IS NULL`.
- **Disconnect-reason analytics:** roll up reasons per conference, per location, per
  hour. Anomalies (sudden spike in `"Media error"`) are often the leading indicator of
  a network or transcoding issue.
- **CRM contact records:** on `disconnected`, look up `remote_alias` against your CRM
  and log a contact record with duration + role.
- **Excluding streaming endpoints:** filter `is_streaming = true` rows out of
  human-attendance counts (otherwise your recorder counts as an attendee).

---

## Reconciliation: missing or out-of-order events

Because deliveries are at-least-once with no ordering guarantee, your handlers will
occasionally see:

| Pattern | Mitigation |
|---|---|
| `disconnected` before `connected` | Process the `disconnected` row as an upsert that may insert a partially-filled row; when `connected` later arrives, its `ON CONFLICT DO NOTHING` is a no-op and the row stays as the `disconnected` handler left it. |
| `connected` but no `disconnected` ever arrives (e.g. Pexip crashed) | Nightly reconciliation job: rows older than N hours with no `disconnected_at` get one synthesised from the conference's `ended_at`, or marked `disconnected_reason = "Unknown — orphaned"`. |
| Two `connected` events for the same `participant_uuid` | Idempotent insert (`ON CONFLICT DO NOTHING`) handles it. Don't bump a counter inside the handler. |
| `participant_updated` arriving before `connected` | Same upsert pattern: write the partial row; the eventual `connected` either fills in or is a no-op. |

The pattern is consistent: **idempotent upserts + a periodic reconciliation pass** is what
keeps the table honest even when the event stream is messy.

---

## Test fixture

As with conference events: capture a real `participant_connected` /
`participant_disconnected` pair from your environment and check them into your project's
test fixtures. If your deployment uses WebRTC apps, capture an `api` + `standard` pair
too — that's the most likely place for a handler bug to creep in unnoticed.
