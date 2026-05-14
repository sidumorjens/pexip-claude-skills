"""Pexip Infinity external policy server — participant avatar lookups against Microsoft Entra."""
from __future__ import annotations

import io
import logging
import os
import secrets
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from PIL import Image

from entra import EntraPhotoClient

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("policy")

POLICY_USER = os.environ["POLICY_USER"]
POLICY_PASS = os.environ["POLICY_PASS"]

entra = EntraPhotoClient(
    tenant_id=os.environ["ENTRA_TENANT_ID"],
    client_id=os.environ["ENTRA_CLIENT_ID"],
    client_secret=os.environ["ENTRA_CLIENT_SECRET"],
    photo_cache_ttl=int(os.getenv("PHOTO_CACHE_TTL", "3600")),
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await entra.aclose()


app = FastAPI(lifespan=lifespan)
security = HTTPBasic()


def check_auth(credentials: HTTPBasicCredentials = Depends(security)) -> None:
    ok = secrets.compare_digest(
        credentials.username, POLICY_USER
    ) and secrets.compare_digest(credentials.password, POLICY_PASS)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
        )


def alias_to_upn(alias: str) -> str | None:
    """`sip:user@domain.com` -> `user@domain.com`; strip URI scheme and SIP params."""
    if not alias:
        return None
    # Drop URI scheme (sip:, sips:, tel:, h323:, etc.)
    if ":" in alias:
        alias = alias.split(":", 1)[1]
    # Drop SIP URI parameters (`user@host;tag=...`)
    alias = alias.split(";", 1)[0]
    alias = alias.strip()
    if "@" not in alias:
        return None
    return alias.lower()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/policy/v1/participant/avatar/{alias:path}")
async def participant_avatar(
    alias: str, request: Request, _: None = Depends(check_auth)
) -> Response:
    try:
        width = int(request.query_params.get("width", 100))
        height = int(request.query_params.get("height", 100))
    except ValueError:
        width = height = 100

    upn = alias_to_upn(alias)
    log.info(
        "avatar request alias=%s upn=%s size=%dx%d", alias, upn, width, height
    )
    if not upn:
        return Response(status_code=404)

    photo_bytes = await entra.get_photo(upn)
    if not photo_bytes:
        return Response(status_code=404)

    try:
        img = Image.open(io.BytesIO(photo_bytes))
        if img.mode != "RGB":
            img = img.convert("RGB")
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        out = io.BytesIO()
        img.save(out, format="JPEG", quality=85)
        return Response(content=out.getvalue(), media_type="image/jpeg")
    except Exception:
        log.exception("failed to process photo for %s", upn)
        return Response(status_code=404)
