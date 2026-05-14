"""Microsoft Entra / Graph client with cached OAuth2 token and photo cache."""
from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass

import httpx

log = logging.getLogger("entra")

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
TOKEN_REFRESH_BUFFER_SECONDS = 60


@dataclass
class _CachedPhoto:
    expires_at: float
    data: bytes | None  # None = negative cache (user has no photo)


class EntraPhotoClient:
    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        photo_cache_ttl: int,
    ) -> None:
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.photo_cache_ttl = photo_cache_ttl

        self._token: str | None = None
        self._token_expires_at: float = 0.0
        self._token_lock = asyncio.Lock()

        self._photo_cache: dict[str, _CachedPhoto] = {}
        self._photo_locks: dict[str, asyncio.Lock] = {}

        # Stay well under Pexip's 5s budget.
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(4.0, connect=1.5))

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _get_token(self, force_refresh: bool = False) -> str:
        now = time.monotonic()
        if (
            not force_refresh
            and self._token
            and now < self._token_expires_at - TOKEN_REFRESH_BUFFER_SECONDS
        ):
            return self._token

        async with self._token_lock:
            now = time.monotonic()
            if (
                not force_refresh
                and self._token
                and now < self._token_expires_at - TOKEN_REFRESH_BUFFER_SECONDS
            ):
                return self._token

            url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "https://graph.microsoft.com/.default",
            }
            log.info("requesting new Entra access token")
            r = await self._client.post(url, data=data)
            r.raise_for_status()
            payload = r.json()
            self._token = payload["access_token"]
            expires_in = int(payload.get("expires_in", 3600))
            self._token_expires_at = time.monotonic() + expires_in
            log.info("got Entra access token, expires in %ds", expires_in)
            return self._token

    async def get_photo(self, upn: str) -> bytes | None:
        cached = self._photo_cache.get(upn)
        if cached and time.monotonic() < cached.expires_at:
            return cached.data

        lock = self._photo_locks.setdefault(upn, asyncio.Lock())
        async with lock:
            cached = self._photo_cache.get(upn)
            if cached and time.monotonic() < cached.expires_at:
                return cached.data

            data = await self._fetch_photo(upn)
            self._photo_cache[upn] = _CachedPhoto(
                expires_at=time.monotonic() + self.photo_cache_ttl,
                data=data,
            )
            return data

    async def _fetch_photo(self, upn: str) -> bytes | None:
        token = await self._get_token()
        url = f"{GRAPH_BASE}/users/{upn}/photo/$value"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            r = await self._client.get(url, headers=headers)
        except httpx.HTTPError as e:
            log.warning("graph photo fetch failed for %s: %s", upn, e)
            return None

        # Token may have been revoked server-side before our local expiry — retry once.
        if r.status_code == 401:
            log.info("graph returned 401, forcing token refresh")
            token = await self._get_token(force_refresh=True)
            try:
                r = await self._client.get(
                    url, headers={"Authorization": f"Bearer {token}"}
                )
            except httpx.HTTPError as e:
                log.warning("graph photo retry failed for %s: %s", upn, e)
                return None

        if r.status_code == 200:
            return r.content
        if r.status_code == 404:
            log.info("no photo in Entra for %s", upn)
            return None
        log.warning("graph photo unexpected status %d for %s: %s", r.status_code, upn, r.text[:200])
        return None
