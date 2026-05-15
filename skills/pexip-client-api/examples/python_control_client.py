"""
Pexip Infinity Client API — control-only client (no media).

End-to-end example that:
  - request_tokens with full state-machine support (PIN, IDP, conference extension, display_name);
  - keeps the token refreshed in the background;
  - exposes typed wrappers for the conference and per-participant actions you're most likely to call;
  - releases cleanly on exit.

Requires: Python 3.10+, httpx>=0.27.
"""

from __future__ import annotations

import asyncio
import logging
import urllib.parse
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

import httpx

log = logging.getLogger("pexip-client")


class PexipError(RuntimeError):
    """Raised when Pexip returns `{"status": "failure", ...}` or an HTTP error."""

    def __init__(self, where: str, body: Any) -> None:
        super().__init__(f"{where}: {body!r}")
        self.where = where
        self.body = body


# A callback type for the join state machine. Implementations of these get
# called when the server prompts the client for additional information.
PromptHandler = Callable[[str, Any], Awaitable[str]]


@dataclass
class Session:
    node: str                                # e.g. "https://conf.example.com"
    alias: str                               # conference alias as-configured
    token: str = ""
    expires: int = 120
    participant_uuid: str = ""
    role: str = "GUEST"                      # HOST or GUEST
    direct_media: bool = False
    current_service_type: str = "conference"
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def base(self) -> str:
        return f"{self.node}/api/client/v2/conferences/{urllib.parse.quote(self.alias, safe='')}"

    @property
    def is_host(self) -> bool:
        return self.role.upper() == "HOST"


# ---------------------------------------------------------------------------
# Low-level HTTP helpers
# ---------------------------------------------------------------------------

async def _request(
    method: str,
    url: str,
    *,
    token: str | None = None,
    json: dict[str, Any] | None = None,
    client: httpx.AsyncClient,
) -> Any:
    """One request → one Pexip envelope. Raises PexipError on non-success."""
    headers = {"token": token} if token else {}
    r = await client.request(method, url, json=json or {}, headers=headers, timeout=15)
    if r.status_code == 503:
        raise PexipError(f"{method} {url}", {"status": r.status_code, "body": r.text})
    try:
        body = r.json()
    except ValueError:
        raise PexipError(f"{method} {url}", f"non-JSON body: {r.text!r}")
    if not isinstance(body, dict) or "status" not in body:
        raise PexipError(f"{method} {url}", f"missing envelope: {body!r}")
    return body                                  # caller decides what to do with status/result


# ---------------------------------------------------------------------------
# Token state machine
# ---------------------------------------------------------------------------

async def request_token(
    node: str,
    alias: str,
    display_name: str,
    *,
    client: httpx.AsyncClient,
    pin_prompt: PromptHandler | None = None,
    sso_prompt: PromptHandler | None = None,
    extension_prompt: PromptHandler | None = None,
    name_prompt: PromptHandler | None = None,
) -> Session:
    """
    Drive the request_token state machine to completion. Returns a populated Session.
    The *_prompt callbacks are awaited only when the server actually asks for input.
    """
    body: dict[str, Any] = {"display_name": display_name}
    base = f"{node}/api/client/v2/conferences/{urllib.parse.quote(alias, safe='')}"

    for _ in range(8):                          # paranoia: cap the loop
        r = await _request("POST", f"{base}/request_token", json=body, client=client)
        result = r.get("result")

        if isinstance(result, dict) and "token" in result:
            sess = Session(
                node=node, alias=alias,
                token=result["token"],
                expires=int(result.get("expires", "120")),
                participant_uuid=result.get("participant_uuid", ""),
                role=result.get("role", "GUEST"),
                direct_media=bool(result.get("direct_media", False)),
                current_service_type=result.get("current_service_type", "conference"),
                raw=result,
            )
            log.info("token issued: uuid=%s role=%s service=%s direct_media=%s",
                     sess.participant_uuid, sess.role, sess.current_service_type, sess.direct_media)
            return sess

        if isinstance(result, dict) and result.get("pin") == "required":
            if not pin_prompt:
                raise PexipError("request_token", "PIN required but no pin_prompt supplied")
            body["pin"] = await pin_prompt("pin", result)
            continue

        if isinstance(result, dict) and "idp" in result:
            if not sso_prompt:
                raise PexipError("request_token", "SSO required but no sso_prompt supplied")
            body["chosen_idp"] = await sso_prompt("choose_idp", result["idp"])
            continue

        if isinstance(result, dict) and "redirect_url" in result:
            if not sso_prompt:
                raise PexipError("request_token", "IDP redirect required but no sso_prompt supplied")
            body["sso_token"] = await sso_prompt("complete_idp", result)
            continue

        if isinstance(result, dict) and "conference_extension" in result:
            if not extension_prompt:
                raise PexipError("request_token", "conference_extension required but no extension_prompt supplied")
            body["conference_extension"] = await extension_prompt("conference_extension", result)
            continue

        if isinstance(result, dict) and result.get("display_name") == "required":
            if not name_prompt:
                raise PexipError("request_token", "display_name required but no name_prompt supplied")
            body["display_name"] = await name_prompt("display_name", result)
            continue

        raise PexipError("request_token", r)

    raise PexipError("request_token", "exceeded prompt iteration cap")


async def refresh_token(sess: Session, *, client: httpx.AsyncClient) -> None:
    """In-place refresh. The new token replaces the old one immediately."""
    body = await _request("POST", f"{sess.base}/refresh_token", token=sess.token, client=client)
    if body.get("status") != "success":
        raise PexipError("refresh_token", body)
    sess.token   = body["result"]["token"]
    sess.expires = int(body["result"].get("expires", sess.expires))
    log.debug("token refreshed, next expiry in %ds", sess.expires)


async def release_token(sess: Session, *, client: httpx.AsyncClient) -> None:
    """Best-effort release. Never raises."""
    try:
        await _request("POST", f"{sess.base}/release_token", token=sess.token, client=client)
    except Exception:
        log.warning("release_token failed; participant will time out naturally", exc_info=True)


# ---------------------------------------------------------------------------
# Background refresher
# ---------------------------------------------------------------------------

@asynccontextmanager
async def auto_refresh(sess: Session, *, client: httpx.AsyncClient):
    """
    Refresh on roughly half-of-expires cadence. Cancels cleanly on exit.
    Use as `async with auto_refresh(sess, client=client): ...`.
    """
    async def loop():
        while True:
            try:
                await asyncio.sleep(max(sess.expires // 2, 15))
                await refresh_token(sess, client=client)
            except asyncio.CancelledError:
                return
            except Exception:
                log.exception("refresh_token failed; will retry next tick")

    task = asyncio.create_task(loop(), name="pexip-refresh")
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


# ---------------------------------------------------------------------------
# Typed wrappers for the most common actions
# ---------------------------------------------------------------------------

async def _post(sess: Session, path: str, body: dict[str, Any] | None = None,
                *, client: httpx.AsyncClient) -> Any:
    r = await _request("POST", f"{sess.base}/{path}", token=sess.token,
                       json=body or {}, client=client)
    if r.get("status") != "success":
        raise PexipError(path, r)
    return r["result"]


async def _get(sess: Session, path: str, *, client: httpx.AsyncClient) -> Any:
    r = await _request("GET", f"{sess.base}/{path}", token=sess.token, client=client)
    if r.get("status") != "success":
        raise PexipError(path, r)
    return r["result"]


# Conference-level
async def conference_status(sess, *, client):  return await _get(sess, "conference_status", client=client)
async def participants(sess, *, client):       return await _get(sess, "participants", client=client)
async def lock(sess, *, client):               return await _post(sess, "lock", client=client)
async def unlock(sess, *, client):             return await _post(sess, "unlock", client=client)
async def mute_guests(sess, *, client):        return await _post(sess, "muteguests", client=client)
async def unmute_guests(sess, *, client):      return await _post(sess, "unmuteguests", client=client)

async def send_message(sess, text: str, *, client):
    return await _post(sess, "message", {"type": "text/plain", "payload": text}, client=client)

async def set_banner(sess, text: str, *, client):
    return await _post(sess, "set_message_text", {"text": text}, client=client)

async def transform_layout(sess, transforms: dict[str, Any], *, client):
    return await _post(sess, "transform_layout", {"transforms": transforms}, client=client)

async def dial(sess, destination: str, *, client,
               role: str = "GUEST", protocol: str = "auto",
               call_type: str = "video", **extras) -> list[str]:
    body = {"destination": destination, "role": role, "protocol": protocol, "call_type": call_type, **extras}
    return await _post(sess, "dial", body, client=client)

# Participant-level
async def participant_mute(sess, uuid: str, *, client):    return await _post(sess, f"participants/{uuid}/mute", client=client)
async def participant_unmute(sess, uuid: str, *, client):  return await _post(sess, f"participants/{uuid}/unmute", client=client)
async def participant_kick(sess, uuid: str, *, client):    return await _post(sess, f"participants/{uuid}/disconnect", client=client)
async def participant_admit(sess, uuid: str, *, client):   return await _post(sess, f"participants/{uuid}/unlock", client=client)
async def participant_role(sess, uuid: str, role: str, *, client):
    return await _post(sess, f"participants/{uuid}/role", {"role": role}, client=client)

async def participant_transfer(sess, uuid: str, dest_alias: str, *, client,
                               role: str = "guest", pin: str | None = None):
    body: dict[str, Any] = {"conference_alias": dest_alias, "role": role}
    if pin is not None:
        body["pin"] = pin
    return await _post(sess, f"participants/{uuid}/transfer", body, client=client)


# ---------------------------------------------------------------------------
# Demo entry point
# ---------------------------------------------------------------------------

async def _demo():
    """End-to-end: lock the room, mute guests, set a banner, list participants, release."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    NODE  = "https://conf.example.com"
    ALIAS = "ops_room"

    async def pin_prompt(_kind, _r):  return "1234"

    async with httpx.AsyncClient() as client:
        sess = await request_token(
            NODE, ALIAS, "Ops Bot",
            client=client,
            pin_prompt=pin_prompt,
        )

        async with auto_refresh(sess, client=client):
            try:
                if not sess.is_host:
                    log.warning("joined as %s — most control actions will fail", sess.role)

                log.info("conference state: %s", await conference_status(sess, client=client))
                await lock(sess, client=client)
                await mute_guests(sess, client=client)
                await set_banner(sess, "Meeting in progress — please be respectful", client=client)

                roster = await participants(sess, client=client)
                log.info("%d participants currently in room", len(roster))

                # Do work …
                await asyncio.sleep(2)

            finally:
                await release_token(sess, client=client)


if __name__ == "__main__":
    asyncio.run(_demo())
