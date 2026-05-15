# Breakout Rooms — Reference

Breakout rooms in Pexip are short-lived child conferences spawned from a
parent. From the Client API perspective, they have two faces:

- **The host's view** — the host stays connected to the main room but
  receives `breakout_*` SSE events on their main-room stream, and can
  drive breakouts via REST.
- **The participant's view** — a guest is *referred* (via the SSE `refer`
  event with a `breakout_name`) to the breakout, joins it with a normal
  `request_token` against the breakout alias, and behaves as if it were a
  normal conference until referred back.

The host can move *their own media* between rooms via `breakout_refer`
events ("Pexip is telling you to drop your media here and bring it up
in breakout X"), but maintains a control session in each room they're
overseeing.

---

## Creating breakouts

### `POST /conferences/<alias>/breakouts`

```jsonc
{
  "name":                    "Discussion 1",
  "duration":                600,                  // seconds; 0 = no auto-end
  "end_action":              "transfer" | "disconnect",
  "participants": {
    "main":                  ["<uuid-of-stay-in-main>", …],
    "<breakout-uuid-1>":     ["<uuid>", "<uuid>"],
    "<breakout-uuid-2>":     ["<uuid>"]
  },
  "guests_allowed_to_leave": true
}
```

- `participants` is a map of **room** to **list of participant UUIDs**. The
  key `"main"` means "keep these in the main room"; other keys are the
  breakout-room UUIDs to create. You can create multiple breakouts in one
  call by adding multiple keys.
- `end_action` controls what happens when `duration` elapses:
  `"transfer"` returns participants to the main room, `"disconnect"` drops
  them.
- `guests_allowed_to_leave: true` lets guests bail out early via
  `POST /conferences/<alias>/leavebreakout` from inside the breakout.

Response:

```json
{ "status": "success",
  "result": { "<breakout-uuid-1>": "<some opaque metadata>", … } }
```

(Exact result shape is sparsely documented; treat it as opaque
confirmation.)

Host-only. Not idempotent — calling twice creates duplicate breakouts.

---

## Host events on the main-room SSE stream

While breakouts are live, the host's main-room `/events` stream carries:

### `breakout_begin`

```json
{ "breakout_uuid": "<uuid>",
  "participant_uuid": "<your control-participant uuid in that breakout>" }
```

Fires when a new breakout exists. The `participant_uuid` is **your** identity
inside that breakout — useful if you want to also `request_token` against
the breakout to drive it directly.

### `breakout_event`

```json
{ "breakout_uuid": "<uuid>",
  "event":         "participant_create",        // any normal event name
  "data":          { …inner event payload… } }
```

Wraps any normal event happening inside a breakout. The host gets a
periscoped view: every participant_create / _update / _delete inside
breakout X gets surfaced as `breakout_event` on the main stream, tagged
with the `breakout_uuid`.

This is the cheap way to monitor breakout activity without
`request_token`-ing into each one.

### `breakout_end`

```json
{ "breakout_uuid": "<uuid>", "participant_uuid": "…" }
```

Breakout closed (either by duration elapsing, by a host calling
`POST /breakouts/<uuid>/disconnect`, or by an explicit "empty" action).

### `breakout_refer`

```json
{ "breakout_uuid": "main" | "<uuid>", "breakout_name": "…" }
```

Pexip is asking the host to **move their media** to the indicated breakout
(or back to `"main"`). Practically:

- Close existing media (`POST /calls/<call_uuid>/disconnect`).
- Open a new media call against the target breakout's session.

For most "monitor only" host bots, you can ignore `breakout_refer` — your
control session stays in the main room and you observe via
`breakout_event`.

---

## Per-breakout host endpoints

All under `/api/client/v2/conferences/<alias>/breakouts/<breakout_uuid>/`,
parallel to the main-room endpoints:

| Endpoint | Mirrors |
|---|---|
| `POST transform_layout` | conference-control's `transform_layout` |
| `POST muteguests` | `muteguests` |
| `POST set_classification_level` | `set_classification_level` |
| `POST disconnect` | Closes this breakout (returns its participants per `end_action`). |
| `POST participants/<uuid>/mute` | Per-participant mute, inside breakout. |
| `POST participants/<uuid>/overlaytext` | Per-participant overlay, inside breakout. |
| `POST clearbreakoutbuzz` | Cancels a "request help" from this breakout. |

The "everyone back to main" shortcut:

```
POST /api/client/v2/conferences/<alias>/breakouts/empty
```

Moves all breakout participants back to the main room and closes every
breakout.

---

## Per-participant breakout actions

### `POST /breakouts/<breakout_uuid>/participants/breakout`

```json
{ "participants": ["<uuid>", "<uuid>"], "destination": "<other-breakout-uuid>" | "main" }
```

Transfer participants between rooms without closing breakouts. Useful for
mid-session shuffles.

### `POST /breakoutbuzz` / `POST /clearbreakoutbuzz`

A participant inside a breakout can "buzz for help" — host's main-room
stream sees it as an event flagged on the breakout. Host clears it with
`/clearbreakoutbuzz` (or the per-breakout variant
`/breakouts/<uuid>/clearbreakoutbuzz`).

### `POST /leavebreakout`

A guest's "leave breakout and return to main" — only valid if the
breakout was created with `guests_allowed_to_leave: true`.

---

## Host control patterns

### Pattern A — Monitor breakouts from the main room

The cheapest host pattern: one SSE connection to the main room, observe
`breakout_*` events, fire REST writes against breakout-scoped endpoints
when needed. No extra tokens.

### Pattern B — Drive a breakout as if it's a separate conference

If you want a richer view of one specific breakout (full participant
list, layout state etc.), call `request_token` against the breakout alias
(if it has one) or use the participant UUID from `breakout_begin` as your
identity. Open a separate `/events` SSE for the breakout.

You'll need a second refresh timer and a second consumer. Worth it only
for deep moderation tooling.

### Pattern C — Move media with the host

If your host is a real human, they generally want to "drop into" a
breakout to coach. That uses `breakout_refer` to move their media. Your
client code: on `breakout_refer`, tear down the current call, set up a
new one against the new room. Maintain control sessions in *both* rooms
during the transition so layout/mute commands keep working.

---

## Gotchas

1. **Breakout UUIDs are not aliases.** They're opaque IDs returned by
   `POST /breakouts`. To send a guest into a breakout via `refer`, Pexip
   handles it server-side — you don't construct the alias yourself.

2. **Each breakout is a real conference.** It has its own
   `conference_status`, its own participant list, its own
   `conference_update` event lifecycle. Reuse all the same client code as
   for the main room when you `request_token` into one.

3. **`end_action` affects user UX.** `"transfer"` is the default-good
   choice for collaborative breakouts; `"disconnect"` makes sense for
   webinar Q&A rooms where you want the participant gone when their
   slot's done.

4. **`POST /breakouts/empty` is a heavy hammer.** It closes every
   breakout in one go, regardless of remaining duration. Use only when
   you mean "session over, regroup".

5. **`breakout_event` doesn't include the breakout name** — only its
   UUID. Cache the name from the corresponding `breakout_begin` if you
   want to display it.
