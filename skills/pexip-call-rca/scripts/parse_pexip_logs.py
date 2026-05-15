#!/usr/bin/env python3
"""
Pexip Infinity log parser for the pexip-call-rca skill.

Reads a single log file, a folder of *.txt / *.log files, or a Pexip support
snapshot tarball / zip, and emits a JSON structured summary on stdout.

Usage:
    parse_pexip_logs.py <path> [--pretty] [--call-id <uuid>]

Output: see schema in skills/pexip-call-rca/SKILL.md §1 step 2.

Stdlib only — runs anywhere Python 3.8+ is available.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tarfile
import tempfile
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

KV_RE = re.compile(r'([A-Za-z][A-Za-z0-9._-]*)="((?:[^"\\]|\\.)*)"')
ISO_TS_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:?\d{2}|Z)?)")
LOG_EXTS = {".txt", ".log"}
SNAPSHOT_DIRS = {"support_log", "developer_log", "administrator_log", "system_logs"}

# Phase classification keyed on (Name prefix, Message substring) → phase tag.
# Order matters: first hit wins.
PHASE_RULES: list[tuple[str, str, str]] = [
    ("support.ice", "", "ice"),
    ("support.crypto", "", "crypto"),
    ("support.media", "", "media"),
    ("support.participant", "Media Stream", "media"),
    ("support.sip", "", "sip"),
    ("administrator.sip", "", "sip"),
    ("support.rest", "", "signaling"),
    ("administrator.conference", "disconnected", "disconnect"),
    ("administrator.conference", "", "signaling"),
    ("support.signaling", "", "signaling"),
    ("connectivity", "", "connectivity"),
]


def classify_phase(name: str, message: str) -> str:
    for name_prefix, msg_sub, phase in PHASE_RULES:
        if name.startswith(name_prefix) and (not msg_sub or msg_sub in message):
            return phase
    return "other"


def unescape(value: str) -> str:
    # Pexip uses \" inside Detail JSON; other backslash escapes are rare.
    return value.replace('\\"', '"').replace("\\\\", "\\")


def parse_line(line: str) -> dict[str, Any] | None:
    """Tokenise one log line into a dict of fields, or None if not a log line."""
    line = line.rstrip("\n")
    m = ISO_TS_RE.match(line)
    if not m:
        return None
    iso_ts = m.group(1)
    fields: dict[str, Any] = {"ts": iso_ts, "raw": line}
    for k, v in KV_RE.findall(line):
        fields[k] = unescape(v)
    if "Level" not in fields and "Name" not in fields:
        # Looks like a timestamp line but no structured fields; treat as orphan.
        return {"ts": iso_ts, "raw": line, "_orphan": True}
    return fields


# ─────────────────────────────────────────────────────────────────────────────
# Input discovery
# ─────────────────────────────────────────────────────────────────────────────

def discover_input(path: Path) -> tuple[str, list[Path], Path | None]:
    """
    Return (kind, list_of_log_files, temp_extraction_dir_or_None).

    kind ∈ {"file", "folder", "tarball", "zip"}.
    Caller is responsible for cleaning up temp dir.
    """
    if not path.exists():
        raise FileNotFoundError(f"path does not exist: {path}")

    if path.is_file():
        suffixes = "".join(path.suffixes).lower()
        if suffixes.endswith((".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".tar")):
            return _extract_tarball(path)
        if suffixes.endswith(".zip"):
            return _extract_zip(path)
        return ("file", [path.resolve()], None)

    if path.is_dir():
        files = sorted(
            p.resolve()
            for p in path.rglob("*")
            if p.is_file() and p.suffix.lower() in LOG_EXTS
        )
        return ("folder", files, None)

    raise ValueError(f"unsupported path: {path}")


def _extract_tarball(path: Path) -> tuple[str, list[Path], Path]:
    tmp = Path(tempfile.mkdtemp(prefix="pexip-rca-"))
    with tarfile.open(path) as tf:
        # Safe extraction: refuse paths that escape the temp dir.
        for member in tf.getmembers():
            target = (tmp / member.name).resolve()
            if not str(target).startswith(str(tmp.resolve()) + os.sep) and target != tmp.resolve():
                raise RuntimeError(f"refusing unsafe tar member: {member.name}")
        tf.extractall(tmp)
    files = sorted(p for p in tmp.rglob("*") if p.is_file() and p.suffix.lower() in LOG_EXTS)
    return ("tarball", files, tmp)


def _extract_zip(path: Path) -> tuple[str, list[Path], Path]:
    tmp = Path(tempfile.mkdtemp(prefix="pexip-rca-"))
    with zipfile.ZipFile(path) as zf:
        for name in zf.namelist():
            target = (tmp / name).resolve()
            if not str(target).startswith(str(tmp.resolve()) + os.sep) and target != tmp.resolve():
                raise RuntimeError(f"refusing unsafe zip member: {name}")
        zf.extractall(tmp)
    files = sorted(p for p in tmp.rglob("*") if p.is_file() and p.suffix.lower() in LOG_EXTS)
    return ("zip", files, tmp)


# ─────────────────────────────────────────────────────────────────────────────
# Line streaming
# ─────────────────────────────────────────────────────────────────────────────

def iter_events(files: list[Path]) -> Iterable[dict[str, Any]]:
    for path in files:
        try:
            with path.open("r", encoding="utf-8", errors="replace") as fh:
                for lineno, raw in enumerate(fh, start=1):
                    parsed = parse_line(raw)
                    if parsed is None:
                        continue
                    parsed["_file"] = str(path)
                    parsed["_line"] = lineno
                    yield parsed
        except OSError as exc:
            # Skip unreadable files but don't fail the whole run.
            yield {
                "ts": "",
                "_file": str(path),
                "_line": 0,
                "_orphan": True,
                "raw": f"<read error: {exc}>",
            }


# ─────────────────────────────────────────────────────────────────────────────
# Per-call aggregation
# ─────────────────────────────────────────────────────────────────────────────

def call_key(event: dict[str, Any]) -> str | None:
    """Pick the most specific call grouping key available on the event.

    Falls back to Participant-Id so failures that fire before a Call-Id has
    been allocated (license check, conference-locked rejection, etc.) still
    group with the participant's join attempt.
    """
    return (
        event.get("Call-Id")
        or event.get("Call-id")
        or event.get("Uuid")
        or event.get("Participant-Id")
    )


_DETAIL_TRUNC = 180


def _truncate(s: str, limit: int = _DETAIL_TRUNC) -> str:
    if len(s) <= limit:
        return s
    return s[:limit] + f"…[+{len(s) - limit} chars]"


def event_summary(event: dict[str, Any]) -> str:
    msg = event.get("Message", "").strip()
    extras: list[str] = []
    for k in (
        "ConferenceAlias",
        "Conference",
        "Protocol",
        "Detail",
        "Reason",
        "Reason-Code",
        "Remote-Candidate-Address",
        "Remote-Candidate-Port",
        "Local-Candidate-Address",
        "Local-Candidate-Port",
        "Local-Candidate-Type",
        "Local-Candidate-Transport",
        "Suite",
        "Mode",
        "Media-Type",
        "Stream-Id",
        "Duration",
    ):
        if k in event:
            val = event[k]
            if isinstance(val, str) and len(val) > _DETAIL_TRUNC:
                val = _truncate(val)
            extras.append(f"{k}={val!r}")
    if extras:
        return msg + " | " + ", ".join(extras)
    return msg


def aggregate(events: Iterable[dict[str, Any]]) -> dict[str, Any]:
    calls: dict[str, dict[str, Any]] = defaultdict(_empty_call)
    level_counter: Counter[str] = Counter()
    component_counter: Counter[str] = Counter()
    orphan_errors: list[dict[str, Any]] = []
    total_lines = 0
    first_ts = ""
    last_ts = ""
    files_seen: set[str] = set()

    for ev in events:
        total_lines += 1
        files_seen.add(ev.get("_file", ""))
        ts = ev.get("ts", "")
        if ts:
            if not first_ts or ts < first_ts:
                first_ts = ts
            if ts > last_ts:
                last_ts = ts

        if ev.get("_orphan"):
            continue

        level = ev.get("Level", "")
        name = ev.get("Name", "")
        msg = ev.get("Message", "")
        if level:
            level_counter[level] += 1
        if name:
            component_counter[name] += 1

        key = call_key(ev)
        if not key:
            # No Call-Id and no Uuid — keep error/warning lines as orphans.
            if level in ("ERROR", "WARNING"):
                orphan_errors.append(_evidence(ev))
            continue

        call = calls[key]
        call["call_id"] = key
        if not call["start"] or ts < call["start"]:
            call["start"] = ts
        if ts > call["end"]:
            call["end"] = ts

        call["conference"] = call["conference"] or ev.get("Conference") or ev.get("ConferenceAlias")
        if "Conference-ID" in ev:
            call["conference_id"] = call["conference_id"] or ev["Conference-ID"]

        protocol = ev.get("Protocol")
        if protocol:
            call["protocols"].add(protocol)

        _maybe_record_participant(call, ev)
        _record_phase_event(call, ev)
        _record_ice(call, ev)
        _record_crypto(call, ev)
        _record_media(call, ev)
        _record_signaling(call, ev)
        _record_disconnect(call, ev)

        if level == "ERROR":
            call["errors"].append(_evidence(ev))
        elif level == "WARNING":
            call["warnings"].append(_evidence(ev))

    summary = {
        "total_lines": total_lines,
        "files": sorted(f for f in files_seen if f),
        "time_span": [first_ts, last_ts] if first_ts else [],
        "levels": dict(level_counter),
        "components": dict(component_counter),
    }

    finalised_calls = [_finalise_call(c) for c in calls.values()]
    finalised_calls.sort(key=lambda c: c.get("start") or "")

    return {
        "summary": summary,
        "calls": finalised_calls,
        "orphan_errors": orphan_errors,
    }


def _empty_call() -> dict[str, Any]:
    return {
        "call_id": "",
        "conference": "",
        "conference_id": "",
        "start": "",
        "end": "",
        "protocols": set(),
        "participants": [],
        "timeline": [],
        "errors": [],
        "warnings": [],
        "ice": {
            "local_candidates": [],
            "remote_candidates": [],
            "selected_pair": None,
        },
        "crypto": {"suites": []},
        "media": {},  # keyed by stream id
        "signaling": {"sip_responses": [], "rest_calls": 0},
        "disconnect": None,
    }


def _evidence(ev: dict[str, Any]) -> dict[str, Any]:
    return {
        "ts": ev.get("ts", ""),
        "file": ev.get("_file", ""),
        "line": ev.get("_line", 0),
        "level": ev.get("Level", ""),
        "component": ev.get("Name", ""),
        "message": ev.get("Message", ""),
        "summary": event_summary(ev),
    }


def _maybe_record_participant(call: dict[str, Any], ev: dict[str, Any]) -> None:
    if ev.get("Message") != "Participant has joined.":
        return
    p_id = ev.get("Participant-Id", "")
    if not p_id or any(p.get("id") == p_id for p in call["participants"]):
        return
    call["participants"].append({
        "id": p_id,
        "name": ev.get("Participant") or ev.get("DisplayName") or "",
        "protocol": ev.get("Protocol", ""),
        "remote_address": ev.get("Remote-Address", ""),
        "vendor": ev.get("Vendor", ""),
        "location": ev.get("Location", ""),
        "joined_at": ev.get("ts", ""),
    })


def _record_phase_event(call: dict[str, Any], ev: dict[str, Any]) -> None:
    name = ev.get("Name", "")
    msg = ev.get("Message", "")
    phase = classify_phase(name, msg)
    call["timeline"].append({
        "ts": ev.get("ts", ""),
        "phase": phase,
        "component": name,
        "event": event_summary(ev),
        "file": ev.get("_file", ""),
        "line": ev.get("_line", 0),
    })


def _record_ice(call: dict[str, Any], ev: dict[str, Any]) -> None:
    if not ev.get("Name", "").startswith("support.ice"):
        return
    msg = ev.get("Message", "")
    if msg == "ICE new-local-candidate event":
        call["ice"]["local_candidates"].append({
            "media": ev.get("Media-Type", ""),
            "stream": ev.get("Stream-Id", ""),
            "component": ev.get("Component-Id", ""),
            "type": ev.get("Local-Candidate-Type", ""),
            "address": ev.get("Local-Candidate-Address", ""),
            "port": ev.get("Local-Candidate-Port", ""),
            "transport": ev.get("Local-Candidate-Transport", ""),
        })
    elif msg == "ICE setting remote candidate":
        call["ice"]["remote_candidates"].append({
            "media": ev.get("Media-Type", ""),
            "stream": ev.get("Stream-Id", ""),
            "component": ev.get("Component-Id", ""),
            "type": ev.get("Remote-Candidate-Type", ""),
            "address": ev.get("Remote-Candidate-Address", ""),
            "port": ev.get("Remote-Candidate-Port", ""),
            "transport": ev.get("Remote-Candidate-Transport", ""),
        })
    elif msg == "ICE new-selected-pair event" and call["ice"]["selected_pair"] is None:
        call["ice"]["selected_pair"] = {
            "ts": ev.get("ts", ""),
            "local": {
                "type": ev.get("Local-Candidate-Type", ""),
                "address": ev.get("Local-Candidate-Address", ""),
                "port": ev.get("Local-Candidate-Port", ""),
                "transport": ev.get("Local-Candidate-Transport", ""),
            },
            "remote": {
                "type": ev.get("Remote-Candidate-Type", ""),
                "address": ev.get("Remote-Candidate-Address", ""),
                "port": ev.get("Remote-Candidate-Port", ""),
                "transport": ev.get("Remote-Candidate-Transport", ""),
            },
        }


def _record_crypto(call: dict[str, Any], ev: dict[str, Any]) -> None:
    if ev.get("Name", "").startswith("support.crypto") and ev.get("Suite"):
        call["crypto"]["suites"].append({
            "ts": ev.get("ts", ""),
            "direction": "encryption" if "encryption" in ev.get("Message", "").lower() else "decryption",
            "suite": ev["Suite"],
        })


_MODE_RE = re.compile(r"^(\S+)\s+\[([^\]]+)\]")


def _record_media(call: dict[str, Any], ev: dict[str, Any]) -> None:
    name = ev.get("Name", "")
    msg = ev.get("Message", "")
    if name == "support.media" and msg == "New mode activated":
        stream_id = ev.get("Stream-Id", "?")
        media_type = ev.get("Media-Type", "")
        mode = ev.get("Mode", "")
        m = _MODE_RE.match(mode)
        codec = m.group(1) if m else mode
        details = m.group(2) if m else ""
        call["media"].setdefault(stream_id, {
            "media_type": media_type,
            "modes": [],
            "destroyed": None,
        })
        call["media"][stream_id]["modes"].append({
            "ts": ev.get("ts", ""),
            "codec": codec,
            "details": details,
            "raw": mode,
        })
    elif name == "support.participant" and msg == "Media Stream destroyed":
        # Detail field contains multi-line stats with literal ^M separators.
        detail = ev.get("Detail", "")
        stream_id = ""
        m = re.match(r"Stream\s+(\d+)\s+\(([^)]+)\)", detail)
        if m:
            stream_id = m.group(1)
            media_type = m.group(2)
        else:
            media_type = ""
        rx = _parse_stats_line(detail, prefix="RX:")
        tx = _parse_stats_line(detail, prefix="TX:")
        call["media"].setdefault(stream_id or "?", {
            "media_type": media_type,
            "modes": [],
            "destroyed": None,
        })
        call["media"][stream_id or "?"]["destroyed"] = {
            "ts": ev.get("ts", ""),
            "media_type": media_type,
            "rx": rx,
            "tx": tx,
        }
    elif name == "support.participant" and msg == "Media Stream created":
        detail = ev.get("Detail", "")
        m = re.match(r"Stream\s+(\d+)\s+\(([^)]+)\)", detail)
        if m:
            stream_id, media_type = m.group(1), m.group(2)
            call["media"].setdefault(stream_id, {
                "media_type": media_type,
                "modes": [],
                "destroyed": None,
            })


def _parse_stats_line(detail: str, prefix: str) -> dict[str, Any] | None:
    # Detail is like "Stream 1 (video)^M   RX: rate 1466kbps loss 0.00% jitter 0ms^M..."
    # In the on-disk log the "^M" is the literal two-character sequence (caret + M),
    # not a CR byte. Pexip writes it that way deliberately so the line stays single-line.
    parts = re.split(r"\^M|\r|\n", detail)
    for line in parts:
        line = line.strip()
        if not line.startswith(prefix):
            continue
        rate = re.search(r"rate\s+(\S+)", line)
        loss = re.search(r"loss\s+(\S+)", line)
        jitter = re.search(r"jitter\s+(\S+)", line)
        return {
            "rate": rate.group(1) if rate else "",
            "loss": loss.group(1) if loss else "",
            "jitter": jitter.group(1) if jitter else "",
        }
    return None


_SIP_RESP_RE = re.compile(r"\b(SIP/2\.0\s+(\d{3})\s+([^\\\"]+))")


def _record_signaling(call: dict[str, Any], ev: dict[str, Any]) -> None:
    name = ev.get("Name", "")
    if name in ("support.sip", "administrator.sip"):
        # Try to pull a SIP response code from the Detail/Message.
        haystack = (ev.get("Detail") or "") + " " + ev.get("Message", "")
        for full, code, phrase in _SIP_RESP_RE.findall(haystack):
            call["signaling"]["sip_responses"].append({
                "ts": ev.get("ts", ""),
                "code": code,
                "phrase": phrase.strip(),
            })
        # Also direct fields used by some Pexip versions.
        if "sip_response_code" in ev:
            call["signaling"]["sip_responses"].append({
                "ts": ev.get("ts", ""),
                "code": ev["sip_response_code"],
                "phrase": ev.get("sip_response_phrase", ""),
            })
    if name == "support.rest":
        call["signaling"]["rest_calls"] += 1


def _record_disconnect(call: dict[str, Any], ev: dict[str, Any]) -> None:
    if ev.get("Message") != "Participant has disconnected.":
        return
    # Keep the *last* disconnect (one event fires per Participant-Id).
    call["disconnect"] = {
        "ts": ev.get("ts", ""),
        "participant_id": ev.get("Participant-Id", ""),
        "protocol": ev.get("Protocol", ""),
        "detail": ev.get("Detail", ""),
        "duration_s": _float_or_none(ev.get("Duration", "")),
        "license_type": ev.get("License-Type", ""),
    }


def _float_or_none(s: str) -> float | None:
    try:
        return float(s) if s else None
    except ValueError:
        return None


def _finalise_call(call: dict[str, Any]) -> dict[str, Any]:
    call["protocols"] = sorted(call["protocols"])
    # Cap timeline to keep JSON manageable; the model can re-Read the source
    # for full lines via the file:line citations.
    if len(call["timeline"]) > 250:
        # Keep first 100, last 100, plus all phase transitions in the middle.
        head = call["timeline"][:100]
        tail = call["timeline"][-100:]
        middle = [e for e in call["timeline"][100:-100] if e["phase"] != "signaling"]
        call["timeline"] = head + middle + tail
        call["timeline_truncated"] = True
    else:
        call["timeline_truncated"] = False
    # Compute derived call type.
    protos = set(call["protocols"])
    if protos == {"API"}:
        # API-only leg with no media counterpart — incomplete log capture.
        call["call_type"] = "API-only"
    elif "WebRTC" in protos and ("SIP" in protos or "H323" in protos):
        call["call_type"] = "Mixed gateway"
    elif "WebRTC" in protos:
        call["call_type"] = "WebRTC"
    elif "SIP" in protos:
        call["call_type"] = "SIP"
    elif "H323" in protos:
        call["call_type"] = "H.323"
    else:
        call["call_type"] = "unknown"
    # Duration shortcut.
    call["duration_s"] = None
    if call["disconnect"] and call["disconnect"].get("duration_s") is not None:
        call["duration_s"] = call["disconnect"]["duration_s"]
    call["disconnect_reason"] = call["disconnect"]["detail"] if call["disconnect"] else ""
    return call


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Pre-parse Pexip Infinity logs for RCA. Emits structured JSON on stdout."
    )
    parser.add_argument("path", help="path to a log file, folder, tarball, or zip")
    parser.add_argument("--pretty", action="store_true", help="pretty-print the JSON")
    parser.add_argument("--call-id", default=None, help="filter output to a single call id")
    args = parser.parse_args(argv)

    path = Path(args.path).expanduser()
    try:
        kind, files, tmp = discover_input(path)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2

    if not files:
        print(
            json.dumps(
                {
                    "input": {"kind": kind, "path": str(path)},
                    "summary": {"total_lines": 0, "files": [], "time_span": [], "levels": {}, "components": {}},
                    "calls": [],
                    "orphan_errors": [],
                    "warning": "no .txt or .log files found",
                },
                indent=2 if args.pretty else None,
            )
        )
        return 0

    result = aggregate(iter_events(files))
    result["input"] = {"kind": kind, "path": str(path)}
    if tmp:
        result["input"]["extracted_to"] = str(tmp)

    if args.call_id:
        result["calls"] = [c for c in result["calls"] if c["call_id"] == args.call_id]

    print(json.dumps(result, indent=2 if args.pretty else None, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
