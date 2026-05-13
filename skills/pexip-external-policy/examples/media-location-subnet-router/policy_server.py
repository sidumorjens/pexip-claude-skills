"""Sample Pexip Infinity External Policy server.

Implements media-location routing based on a configurable IP-subnet → Infinity
location mapping. The other five policy endpoints are stubbed to pass through
(action=continue, empty result) so the server is safe to attach to a full
policy profile in Pexip admin.

Run:
    POLICY_USER=pexip POLICY_PASS=changeme \
        uvicorn policy_server:app --host 0.0.0.0 --port 8080
"""

from __future__ import annotations

import ipaddress
import json
import logging
import os
import secrets
import tempfile
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field, field_validator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("policy")

POLICY_USER = os.environ.get("POLICY_USER", "pexip")
POLICY_PASS = os.environ.get("POLICY_PASS", "changeme")
SUBNET_MAP_PATH = Path(os.environ.get("SUBNET_MAP_PATH", "subnet_map.json"))

app = FastAPI(title="Pexip Subnet → Media Location Policy")
security = HTTPBasic()


# --------------------------------------------------------------------------- #
# Subnet map
# --------------------------------------------------------------------------- #


class SubnetMap:
    """IP-subnet → Pexip location lookup with longest-prefix match."""

    def __init__(self) -> None:
        self.default_location: str = ""
        self.default_overflow: list[str] = []
        # Stored sorted by prefix length descending so the first match wins.
        self.entries: list[
            tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, dict[str, Any]]
        ] = []

    def load(self, path: Path) -> None:
        raw = json.loads(path.read_text())
        self.default_location = raw["default_location"]
        self.default_overflow = list(raw.get("default_overflow_locations", []))

        entries = []
        for m in raw.get("mappings", []):
            net = ipaddress.ip_network(m["subnet"], strict=False)
            entries.append((net, m))
        # Longest prefix first; ties broken by network address for determinism.
        entries.sort(key=lambda e: (-e[0].prefixlen, int(e[0].network_address)))
        self.entries = entries
        log.info(
            "Loaded subnet map: %d entries, default=%s overflow=%s",
            len(self.entries),
            self.default_location,
            self.default_overflow,
        )

    def lookup(self, ip_str: str) -> tuple[str, list[str], str | None]:
        """Return (location, overflow_locations, matched_subnet_or_None)."""
        if not ip_str:
            return self.default_location, self.default_overflow, None
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            log.warning("Unparseable remote_address=%r — using default", ip_str)
            return self.default_location, self.default_overflow, None

        for net, entry in self.entries:
            if ip.version != net.version:
                continue
            if ip in net:
                return (
                    entry["location"],
                    list(entry.get("overflow_locations", [])),
                    str(net),
                )
        return self.default_location, self.default_overflow, None


subnet_map = SubnetMap()


@app.on_event("startup")
def _load_map() -> None:
    subnet_map.load(SUBNET_MAP_PATH)


# --------------------------------------------------------------------------- #
# Auth
# --------------------------------------------------------------------------- #


def check_auth(credentials: HTTPBasicCredentials = Depends(security)) -> None:
    ok_user = secrets.compare_digest(credentials.username, POLICY_USER)
    ok_pass = secrets.compare_digest(credentials.password, POLICY_PASS)
    if not (ok_user and ok_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )


# --------------------------------------------------------------------------- #
# Policy endpoints
# --------------------------------------------------------------------------- #


@app.get("/policy/v1/service/configuration")
async def service_configuration(request: Request, _: None = Depends(check_auth)):
    log.info(
        "service_configuration local=%s remote=%s → continue (use DB)",
        request.query_params.get("local_alias"),
        request.query_params.get("remote_alias"),
    )
    return JSONResponse({"status": "success", "action": "continue", "result": {}})


@app.get("/policy/v1/participant/properties")
async def participant_properties(request: Request, _: None = Depends(check_auth)):
    log.info(
        "participant_properties uuid=%s alias=%s → continue",
        request.query_params.get("participant_uuid"),
        request.query_params.get("remote_alias"),
    )
    return JSONResponse({"status": "success", "action": "continue", "result": {}})


@app.get("/policy/v1/participant/location")
async def media_location(request: Request, _: None = Depends(check_auth)):
    remote_ip = request.query_params.get("remote_address", "")
    requesting_location = request.query_params.get("location", "")

    location, overflow, matched = subnet_map.lookup(remote_ip)

    log.info(
        "media_location remote_ip=%s requesting_node_location=%s → location=%s "
        "overflow=%s matched_subnet=%s",
        remote_ip,
        requesting_location,
        location,
        overflow,
        matched,
    )

    return JSONResponse(
        {
            "status": "success",
            "result": {
                "location": location,
                "overflow_locations": overflow,
            },
            # Extra keys are surfaced in Pexip's support log — handy for forensics.
            "reason": (
                f"matched {matched}" if matched else "no subnet match — using default"
            ),
        }
    )


@app.get("/policy/v1/participant/avatar/{alias:path}")
async def participant_avatar(alias: str, _: None = Depends(check_auth)):
    # 404 → Pexip falls back to its own avatar handling.
    return Response(status_code=404)


@app.get("/policy/v1/registrations")
async def directory_information(_: None = Depends(check_auth)):
    return JSONResponse({"status": "success", "result": []})


@app.get("/policy/v1/registrations/{alias:path}")
async def registration_alias(alias: str, _: None = Depends(check_auth)):
    return JSONResponse({"status": "success", "action": "continue", "result": {}})


# --------------------------------------------------------------------------- #
# Admin / ops
# --------------------------------------------------------------------------- #


@app.get("/health")
async def health():
    return {"status": "ok", "subnet_map_entries": len(subnet_map.entries)}


@app.post("/admin/reload")
async def reload_map(_: None = Depends(check_auth)):
    subnet_map.load(SUBNET_MAP_PATH)
    return {"status": "ok", "subnet_map_entries": len(subnet_map.entries)}


@app.get("/admin/lookup")
async def admin_lookup(ip: str, _: None = Depends(check_auth)):
    """Test the subnet map without involving Pexip."""
    location, overflow, matched = subnet_map.lookup(ip)
    return {
        "ip": ip,
        "matched_subnet": matched,
        "location": location,
        "overflow_locations": overflow,
    }


# --------------------------------------------------------------------------- #
# Config edit API (used by the web UI)
# --------------------------------------------------------------------------- #


class MappingModel(BaseModel):
    subnet: str
    location: str = Field(min_length=1)
    overflow_locations: list[str] = []
    description: str = ""

    @field_validator("subnet")
    @classmethod
    def _valid_cidr(cls, v: str) -> str:
        try:
            ipaddress.ip_network(v, strict=False)
        except ValueError as e:
            raise ValueError(f"invalid CIDR {v!r}: {e}") from e
        return v


class ConfigModel(BaseModel):
    default_location: str = Field(min_length=1)
    default_overflow_locations: list[str] = []
    mappings: list[MappingModel] = []


@app.get("/admin/config")
async def get_config(_: None = Depends(check_auth)):
    return json.loads(SUBNET_MAP_PATH.read_text())


@app.put("/admin/config")
async def put_config(cfg: ConfigModel, _: None = Depends(check_auth)):
    payload = cfg.model_dump()
    # Atomic write: temp file in same directory, fsync, rename.
    target = SUBNET_MAP_PATH.resolve()
    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=str(target.parent),
        prefix=f".{target.name}.",
        suffix=".tmp",
        delete=False,
    )
    try:
        json.dump(payload, tmp, indent=2)
        tmp.write("\n")
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp.close()
        os.replace(tmp.name, target)
    except Exception:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass
        raise
    subnet_map.load(SUBNET_MAP_PATH)
    return {"status": "ok", "subnet_map_entries": len(subnet_map.entries)}


# --------------------------------------------------------------------------- #
# Web UI
# --------------------------------------------------------------------------- #


UI_PATH = Path(__file__).parent / "admin_ui.html"


@app.get("/")
async def root_redirect():
    # Convenience: send people to the UI.
    return Response(status_code=307, headers={"Location": "/admin/ui"})


@app.get("/admin/ui")
async def admin_ui(_: None = Depends(check_auth)):
    return FileResponse(UI_PATH, media_type="text/html")
