"""
Pexip Infinity Client API — SSE listener with reconnect.

A long-lived consumer of the /events stream that:
  - drives request_token (reusing the helpers in python_control_client.py);
  - parses the SSE stream manually (no third-party SSE library);
  - tracks the participant_sync_begin/_end bracket and maintains a live roster;
  - watchdog-times-out idle connections and reconnects with exponential backoff;
  - re-runs request_token on 401, refresh_token on a separate timer otherwise;
  - dispatches every documented event name through a handler registry.

Requires: Python 3.10+, httpx>=0.27.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any, Awaitable, Callable

import httpx

from python_control_client import (
    PexipError,
    Session,
    refresh_token,
    request_token,
)

log = logging.getLogger("pexip-sse")


EventHandler = Callable[[str, dict[str, Any] | None], Awaitable[None]]


# ---------------------------------------------------------------------------
# SSE parser
# ---------------------------------------------------------------------------

async def _iter_sse(response: httpx.Response):
    """
    Yields (event_name, data_str). data_str may be empty.
    Handles multi-line `data:` and comment lines correctly.
    """
    event_name = "message"
    data_lines: list[str] = []
    async for raw in response.aiter_lines():
        line = raw.rstrip("\r")
        if line == "":
            data = "\n".join(data_lines)
            if event_name or data:
                yield event_name, data
            event_name, data_lines = "message", []
            continue
        if line.startswith(":"):                # comment / heartbeat
            continue
        if ":" in line:
            field, _, value = line.partition(":")
            if value.startswith(" "):
                value = value[1:]
            if field == "event":
                event_name = value
            elif field == "data":
                data_lines.append(value)
            elif field == "id":
                pass                            # Pexip doesn't send these; ignore if it ever does
            elif field == "retry":
                pass


# ---------------------------------------------------------------------------
# Roster tracker
# ---------------------------------------------------------------------------

class Roster:
    """In-memory participant list, atomically rebuilt on every sync bracket."""

    def __init__(self) -> None:
        self.participants: dict[str, dict[str, Any]] = {}
        self._in_sync = False
        self._seen: set[str] = set()

    def begin_sync(self) -> None:
        self._in_sync = True
        self._seen = set()

    def end_sync(self) -> None:
        self.participants = {u: p for u, p in self.participants.items() if u in self._seen}
        self._in_sync = False
        log.info("roster reconciled, %d participant(s)", len(self.participants))

    def upsert(self, p: dict[str, Any]) -> None:
        uuid = p.get("uuid")
        if not uuid:
            return
        self.participants[uuid] = p
        if self._in_sync:
            self._seen.add(uuid)

    def delete(self, uuid: str) -> None:
        self.participants.pop(uuid, None)


# ---------------------------------------------------------------------------
# SSE consumer with reconnect + watchdog
# ---------------------------------------------------------------------------

WATCHDOG_SECONDS = 90
BACKOFF_INITIAL  = 1.0
BACKOFF_MAX      = 30.0


async def consume_events(
    sess: Session,
    handle: EventHandler,
    roster: Roster | None,
    *,
    client: httpx.AsyncClient,
    on_reauth: Callable[[], Awaitable[Session]] | None = None,
) -> None:
    """
    Run forever (until cancelled). Handles reconnect, watchdog, 401 → re-auth.
    """
    backoff = BACKOFF_INITIAL
    while True:
        url = f"{sess.base}/events?token={sess.token}"
        try:
            log.info("connecting SSE to %s", sess.base)
            last_byte = time.monotonic()

            async with client.stream("GET", url, headers={"Accept": "text/event-stream"},
                                     timeout=None) as r:
                if r.status_code == 401:
                    log.warning("SSE returned 401 — re-authenticating")
                    if not on_reauth:
                        raise PexipError("events", "401 and no on_reauth handler")
                    sess = await on_reauth()
                    continue

                r.raise_for_status()
                backoff = BACKOFF_INITIAL
                log.info("SSE connected")

                async def watchdog():
                    while True:
                        await asyncio.sleep(5)
                        if time.monotonic() - last_byte > WATCHDOG_SECONDS:
                            log.warning("SSE watchdog: no data for %ds, dropping", WATCHDOG_SECONDS)
                            await r.aclose()
                            return

                wd = asyncio.create_task(watchdog(), name="pexip-sse-watchdog")
                try:
                    async for event_name, data_str in _iter_sse(r):
                        last_byte = time.monotonic()
                        payload: dict[str, Any] | None = None
                        if data_str and data_str != "null":
                            try:
                                payload = json.loads(data_str)
                            except ValueError:
                                log.warning("non-JSON SSE payload for %s: %r", event_name, data_str)

                        # Roster bookkeeping
                        if roster is not None:
                            if event_name == "participant_sync_begin":
                                roster.begin_sync()
                            elif event_name == "participant_sync_end":
                                roster.end_sync()
                            elif event_name in ("participant_create", "participant_update") and payload:
                                roster.upsert(payload)
                            elif event_name == "participant_delete" and payload:
                                roster.delete(payload.get("uuid", ""))

                        await handle(event_name, payload)
                finally:
                    wd.cancel()

        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("SSE error; reconnecting in %.1fs", backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, BACKOFF_MAX)


# ---------------------------------------------------------------------------
# Default dispatcher
# ---------------------------------------------------------------------------

HANDLERS: dict[str, EventHandler] = {}

def on(event_name: str):
    def deco(fn: EventHandler) -> EventHandler:
        HANDLERS[event_name] = fn
        return fn
    return deco


async def default_handler(event_name: str, data: dict[str, Any] | None) -> None:
    fn = HANDLERS.get(event_name)
    if fn:
        await fn(event_name, data)
    else:
        log.debug("ignoring unknown/unhandled event %s data=%s", event_name, data)


@on("participant_create")
async def _pc(_n, p):
    log.info("+ participant: uuid=%s name=%s role=%s",
             p and p.get("uuid"), p and p.get("display_name"), p and p.get("role"))


@on("participant_delete")
async def _pd(_n, p):
    log.info("- participant: uuid=%s", p and p.get("uuid"))


@on("conference_update")
async def _cu(_n, c):
    if not c:
        return
    log.info("conference state: locked=%s muted=%s started=%s recording=%s streaming=%s",
             c.get("locked"), c.get("guests_muted"), c.get("started"),
             c.get("recording"), c.get("streaming"))


@on("disconnect")
async def _d(_n, d):
    log.warning("Pexip is disconnecting us: %s", d and d.get("reason"))


@on("refer")
async def _r(_n, d):
    log.warning("Pexip referring us to alias=%s breakout=%s",
                d and d.get("alias"), d and d.get("breakout_name"))


@on("message_received")
async def _msg(_n, m):
    if not m:
        return
    arrow = "→" if m.get("direct") else "⇒"
    log.info("chat %s %s [%s]: %s", m.get("origin"), arrow, m.get("type"), m.get("payload"))


# ---------------------------------------------------------------------------
# Demo entry point
# ---------------------------------------------------------------------------

async def _demo():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    NODE  = "https://conf.example.com"
    ALIAS = "ops_room"

    async with httpx.AsyncClient() as client:
        sess = await request_token(NODE, ALIAS, "Monitor Bot", client=client)
        roster = Roster()

        async def reauth() -> Session:
            return await request_token(NODE, ALIAS, "Monitor Bot", client=client)

        async def refresher():
            while True:
                await asyncio.sleep(max(sess.expires // 2, 15))
                try:
                    await refresh_token(sess, client=client)
                except Exception:
                    log.exception("refresh failed")

        tasks = [
            asyncio.create_task(refresher(), name="refresher"),
            asyncio.create_task(consume_events(sess, default_handler, roster,
                                               client=client, on_reauth=reauth)),
        ]
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            pass
        finally:
            for t in tasks:
                t.cancel()


if __name__ == "__main__":
    asyncio.run(_demo())
