# Participant Events — Reference

The **participant lifecycle** class of Pexip Infinity event sink events. Fired by a
Transcoding Conferencing Node when a participant joins a conference, changes state
mid-call, or disconnects.

> **Sourcing:** field set below comes from a production receiver's Pydantic model of
> the participant `data` block — every field listed has been seen in real traffic on
> v2 event sinks. Older v1 deployments may differ in some field names.

---

## Events in this class

| Event | When it fires |
|---|---|
| `participant_connected` | A participant has joined a conference. For WebRTC + SSO this is after authentication; for SIP/H.323, after any PIN entry. |
| `participant_updated` | A participant's attributes change — mute, role, presenting flag, bandwidth, layout group, etc. Carries only the changed fields. |
| `participant_disconnected` | A participant has left the conference. Includes a disconnect reason. |

Related (covered briefly in SKILL.md §2 rather than here):

- `participant_media_stream_window` — mid-call quality classification change.
- `participant_media_streams_destroyed` — end-of-call media stats.

---

## Envelope

Every event arrives in the same v2 envelope (see SKILL.md §1):

```json
{
  "node": "10.44.34.11",
  "seq": 689,
  "version": 2,
  "time": 1606392917.976155,
  "event": "participant_connected",
  "data": { /* participant-specific fields below */ }
}
```

Correlation:

- Participant identity = `data.uuid`.
- The conference they belong to = `data.conference` (matches `data.name` on `conference_*` events).

---

## `data` fields

Confirmed against a production receiver. Most fields are optional; treat absence as "no
change" on `participant_updated`, and as "unknown" (don't synthesise a default) on
`participant_connected`.

### Identity

| Field | Type | Notes |
|---|---|---|
| `uuid` | String (UUID) | **The participant identity key.** Stable for this participant's session in this conference. Use to join `connected` → `disconnected`. |
| `conference` | String | Name of the conference this participant is in. Matches `data.name` on conference events — use to join into the conference record. |
| `display_name` | String | Display name shown in the conference. May have been overridden by External Policy. Coalesce missing/empty to `"Unknown"`. |
| `source_alias` | String | Alias the participant dialled in as (i.e. "from"). |
| `destination_alias` | String | Alias they dialled (i.e. "to"). |
| `remote_address` | String | IP address of the participant's endpoint. |
| `call_id` | String | Call-leg identifier. |
| `conversation_id` | String | Conversation identifier (cross-protocol). |
| `call_tag` | String | Operator-assigned per-call tag. |
| `related_uuids` | List of strings | Other participant UUIDs related to this one — used for transfers, breakout-room linking, and host "shadow" entries. |

### Call properties

| Field | Type | Notes |
|---|---|---|
| `role` | String | `"chair"`, `"guest"`, or `"unknown"`. |
| `protocol` | String | `"webrtc"`, `"sip"`, `"h323"`, `"rtmp"`, `"teams"`, `"mssip"`, `"api"`. |
| `vendor` | String | Endpoint vendor/version string. |
| `call_direction` | String | `"inbound"` / `"outbound"` (dial-in vs. dial-out). |
| `encryption` | String | Media encryption status. |
| `service_type` | String | The service type as inherited from the conference (`conference`, `gateway`, etc. — see conference-events.md). |
| `service_tag` | String | The service tag from the conference. Convenient for per-participant billing aggregation without joining. |
| `is_idp_authenticated` | Boolean | Whether the IdP attested to the display name (WebRTC + SSO). |

### State (mostly seen on `participant_updated`)

| Field | Type | Notes |
|---|---|---|
| `is_muted` | Boolean | **Admin-muted** (someone with control muted them). |
| `is_client_muted` | Boolean | **Self-muted** (they muted themselves). |
| `is_presenting` | Boolean | Currently sending presentation content. |
| `is_streaming` | Boolean | Streaming/recording endpoint (i.e. not a human). Filter these out of attendance counts. |
| `has_media` | Boolean | **Whether the participant is actually carrying media in this conference.** Critical for breakout-room rosters — host "shadow" entries appear in every room they monitor but have `has_media: false` for all except the one they're actually in. |

### Bandwidth & media routing

| Field | Type | Notes |
|---|---|---|
| `rx_bandwidth` | Number | Receive bandwidth. |
| `tx_bandwidth` | Number | Transmit bandwidth. |
| `media_node` | String | IP / identifier of the Conferencing Node handling this participant's media. |
| `signalling_node` | String | IP / identifier of the node handling signalling. |
| `proxy_node` | String | IP / identifier of the Proxying Edge Node (if applicable). |
| `system_location` | String | The Pexip system location the participant is using. |
| `call_quality` | String | One of `"0_unknown"`, `"1_good"`, `"2_ok"`, `"3_bad"`, `"4_terrible"`. Updated by `participant_media_stream_window` events. |
| `license_count` | Number | Licenses consumed by this participant. |

### Timing & disconnect

| Field | Type | Notes |
|---|---|---|
| `connect_time` | Float (epoch seconds) | When the participant connected. **May be `null` on breakout transfers** — defensive code: `connect_time = d.get("connect_time") or fallback`. |
| `disconnect_time` / `end_time` | Float (epoch seconds) | (on `disconnected`) When they left. Some payloads use `end_time` for this — handle both. |
| `duration` | Float (seconds) | (on `disconnected`) Convenience field; useful when `connect_time` was null on transfer. |
| `disconnect_reason` | String | (on `disconnected`) Vendor-supplied string. See below. |

---

## `disconnect_reason` values

Pexip emits these as free-form strings, and the set evolves with versions. Real-world
behaviour:

- Common values include `"User initiated"`, `"Owner initiated"`, `"Conference ended"`, `"Waiting for host expired"`, `"PIN entry failed"`, `"Conference full"`, `"Media error"`, `"Network error"`, `"Timeout"`.
- Handlers should **persist whatever string arrives** and not normalise. Treat unknown values as `"Unknown — <raw string>"` for analytics rather than dropping them.
- For per-conference cohort analysis, group reasons into buckets (`user_ended`, `system_ended`, `error`, `timeout`, `other`) and keep the raw value in a separate column.

---

## Worked examples

### `participant_connected`

```json
{
  "node": "10.44.34.11",
  "seq": 2,
  "version": 2,
  "time": 1747218005.0,
  "event": "participant_connected",
  "data": {
    "uuid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "conference": "meet.alice",
    "display_name": "Alice",
    "source_alias": "sip:alice@example.com",
    "destination_alias": "meet.alice",
    "remote_address": "10.20.30.40",
    "role": "chair",
    "protocol": "sip",
    "call_direction": "inbound",
    "vendor": "Cisco/CE",
    "encryption": "On",
    "service_type": "conference",
    "service_tag": "alice-vmr",
    "media_node": "10.44.34.11",
    "signalling_node": "10.44.34.11",
    "system_location": "London",
    "connect_time": 1747218005.0,
    "has_media": true,
    "is_streaming": false,
    "is_muted": false,
    "is_client_muted": false
  }
}
```

Handler:

```python
@handler("participant_connected")
async def on_p_connect(envelope: dict):
    d = envelope["data"]
    if not d.get("uuid") or not d.get("conference"):
        log.warning("participant_connected missing uuid or conference")
        return
    async with store_lock:
        conf = store.get(d["conference"])
        if conf is None:
            # Race: participant arrived before conference_started
            conf = Conference(name=d["conference"], is_started=True,
                              service_type=d.get("service_type", "conference"))
            store[d["conference"]] = conf
        conf.participants[d["uuid"]] = build_participant(d)
```

### `participant_updated`

Carries only the changed fields. Apply as a partial update:

```json
{
  "node": "10.44.34.11",
  "seq": 47,
  "version": 2,
  "time": 1747218300.5,
  "event": "participant_updated",
  "data": {
    "uuid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "conference": "meet.alice",
    "is_presenting": true,
    "tx_bandwidth": 1850000
  }
}
```

```python
_MUTABLE_FIELDS = (
    "is_muted", "is_client_muted", "is_presenting", "is_streaming",
    "has_media", "display_name", "role", "vendor",
    "rx_bandwidth", "tx_bandwidth", "encryption",
)

@handler("participant_updated")
async def on_p_update(envelope: dict):
    d = envelope["data"]
    conf = store.get(d.get("conference"))
    if not conf:
        return
    p = conf.participants.get(d.get("uuid"))
    if not p:
        # First time seeing this participant (missed connected) — build from what we have
        p = build_participant(d)
        conf.participants[d["uuid"]] = p
        return
    for k in _MUTABLE_FIELDS:
        if k in d:
            setattr(p, k, d[k])
```

### `participant_disconnected`

```json
{
  "node": "10.44.34.11",
  "seq": 198,
  "version": 2,
  "time": 1747219934.2,
  "event": "participant_disconnected",
  "data": {
    "uuid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "conference": "meet.alice",
    "end_time": 1747219934.0,
    "duration": 1929.0,
    "disconnect_reason": "User initiated"
  }
}
```

Handler — note `end_time` and `disconnect_time` are both seen in the wild:

```python
@handler("participant_disconnected")
async def on_p_disconnect(envelope: dict):
    d = envelope["data"]
    conf = store.get(d.get("conference"))
    if not conf:
        return
    p = conf.participants.pop(d.get("uuid"), None)
    if p:
        p.disconnect_time = d.get("end_time") or d.get("disconnect_time")
        p.disconnect_reason = d.get("disconnect_reason")
        p.duration = d.get("duration")
        await persist_attendance(p, conf.name)
```

---

## `has_media` and breakout host shadows

A host monitoring multiple breakout rooms appears as a participant in **every** room
they're monitoring — but only one of those participant records has `has_media: true`
(the room they're actually in). The others are "shadow" entries used by Pexip to track
the monitoring relationship.

For dashboards and rosters, **filter on `has_media: true`** when displaying "actually
present" participants. For attendance/billing, decide whether to count shadows (probably
not for human-attendance metrics).

---

## WebRTC two-stage joins

For Pexip's WebRTC apps, a single user join may produce **two** `participant_connected`
events in quick succession — first with `protocol: "api"`, then with the real protocol
(`"webrtc"`). Decide per use case:

- For analytics/billing: count only the non-`api` entry.
- For dashboard rosters: ignore the `api` entry; it doesn't represent a visible user.
- The two entries are linked via `related_uuids` — use that to attribute them to the same logical user when needed.

---

## `participant_media_stream_window` (call quality changes)

Mid-call, Pexip emits quality classification updates as a separate event:

```json
{
  "node": "10.44.34.11",
  "seq": 412,
  "version": 2,
  "time": 1747218600.0,
  "event": "participant_media_stream_window",
  "data": {
    "uuid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "call_quality_now": "3_bad"
  }
}
```

Apply by patching the participant record:

```python
@handler("participant_media_stream_window")
async def on_quality(envelope: dict):
    d = envelope["data"]
    # The event doesn't carry the conference name — search by uuid.
    for conf in store.values():
        p = conf.participants.get(d.get("uuid"))
        if p:
            p.call_quality = d.get("call_quality_now")
            return
```

---

## Common processing patterns

- **Attendance row per participant:** keyed on `uuid`, inserted on `connected`, updated on `disconnected`. Join to `conference` on `data.conference == conference.name`.
- **Real-time roster:** maintain `{conference_name: {uuid: Participant}}` for a live dashboard. Filter on `has_media` for "actually present". Cold-start by querying rows where `disconnected_at IS NULL`.
- **Disconnect-reason analytics:** roll up reasons per conference, per location, per hour. A sudden spike in `"Media error"` or `"Network error"` is often the leading indicator of a transcoding/network incident.
- **Excluding streaming endpoints from human counts:** filter `is_streaming = true` rows out of attendance metrics.
- **Per-location capacity:** group by `system_location` + `media_node` from `participant_connected` events to derive per-location concurrent participants.

---

## Reconciliation: missing or out-of-order events

At-least-once delivery + no cross-node ordering means your handlers will occasionally see:

| Pattern | Mitigation |
|---|---|
| `disconnected` before `connected` | Handle by upserting the participant row in `disconnected` (with the timing fields it provides); when `connected` arrives, its insert is a no-op. |
| `connected` but no `disconnected` ever arrives (Pexip restart, receiver outage) | Periodic reconciliation: rows older than N hours with no `disconnected_at` get one synthesised from the conference's `ended_at`, or `disconnect_reason = "Unknown — orphaned"`. |
| Two `connected` events for the same `uuid` | Idempotent insert (`ON CONFLICT (uuid) DO NOTHING`) handles it. Don't bump a counter inside the handler. |
| `participant_updated` before `connected` | Same upsert pattern — write the partial row; the eventual `connected` either fills in or is a no-op. |
| Quality event before `connected` | Search-by-uuid will miss; either persist a deferred-quality record keyed on uuid and apply when `connected` arrives, or accept that early quality data is occasionally lost. |

The pattern is consistent: **idempotent upserts + a periodic reconciliation pass** is what
keeps the table honest even when the event stream is messy. Combined with the
`(node, seq)` dedup from SKILL.md §4, all handlers are safe to run repeatedly on the same
input.

---

## Test fixture

Capture a real `participant_connected` / `participant_disconnected` pair from your
environment. If your deployment uses WebRTC apps, capture an `api` + real-protocol pair
too — that's the most likely place for a handler bug to creep in. If you use breakout
rooms, capture a participant with `has_media: false` so the filter logic is tested.
