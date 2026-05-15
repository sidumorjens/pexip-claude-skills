"""Parse the saved Pexip Infinity 'API Schemas' HTML into per-resource markdown.

Input:  ../API Schemas _ Pexip Infinity.html
Output: ../references/<section>/<resource>.md  + ../references/INDEX.md
"""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "API Schemas _ Pexip Infinity.html"
OUT_DIR = ROOT / "references"

SECTIONS = {
    "Configuration": "configuration",
    "Status": "status",
    "Commands": "command",
    "History": "history",
    "Embedded Resources": "embedded",
    "Responses": "responses",
}


class SchemaParser(HTMLParser):
    """Walks the HTML and emits one dict per <div class='module'>."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.section: str | None = None
        self.modules: list[dict] = []
        self.cur: dict | None = None

        # capture state
        self._in_h3 = False
        self._h3_buf = []

        self._in_h2 = False
        self._h2_buf = []

        # table-cell capture
        self._in_td = False
        self._in_th = False
        self._cell_buf: list[str] = []
        self._cell_link: str | None = None  # text inside <a> while in a td

        # row state
        self._row_cells: list[dict] = []
        self._row_class: str | None = None

        # which table column type we're in (for type-cell links)
        self._in_a = False
        self._a_text_buf: list[str] = []

    # ---- tag handlers --------------------------------------------------
    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)

        if tag == "h3":
            self._in_h3 = True
            self._h3_buf = []
            return

        if tag == "div" and attrs_d.get("class") == "module":
            # start of a new resource
            self.cur = {
                "section": self.section,
                "path": None,
                "title": None,
                "methods": [],  # list of (label, value)
                "fields": [],   # list of dicts
            }
            return

        if tag == "a" and "name" in attrs_d and self.cur is not None and self.cur["path"] is None:
            self.cur["path"] = attrs_d["name"]
            return

        if tag == "h2" and self.cur is not None and self.cur["path"] is None:
            # fallback if name= came as separate <a>
            self._in_h2 = True
            self._h2_buf = []
            return

        if tag == "tr":
            self._row_cells = []
            self._row_class = attrs_d.get("class")
            return

        if tag == "th":
            self._in_th = True
            self._cell_buf = []
            return

        if tag == "td":
            self._in_td = True
            self._cell_buf = []
            self._cell_link = None
            return

        if tag == "a" and self._in_td:
            self._in_a = True
            self._a_text_buf = []
            return

    def handle_endtag(self, tag):
        if tag == "h3":
            self._in_h3 = False
            text = "".join(self._h3_buf).strip()
            if text in SECTIONS:
                self.section = text
            return

        if tag == "h2" and self._in_h2:
            self._in_h2 = False
            if self.cur is not None and self.cur["path"] is None:
                self.cur["path"] = "".join(self._h2_buf).strip()
            return

        if tag == "a" and self._in_a:
            self._in_a = False
            link_text = "".join(self._a_text_buf).strip()
            if link_text:
                self._cell_link = link_text
            return

        if tag == "th":
            self._in_th = False
            self._row_cells.append({"kind": "th", "text": "".join(self._cell_buf).strip()})
            return

        if tag == "td":
            self._in_td = False
            text = "".join(self._cell_buf).strip()
            cell = {"kind": "td", "text": text, "link": self._cell_link}
            self._row_cells.append(cell)
            return

        if tag == "tr":
            self._finish_row()
            return

        if tag == "div" and self.cur is not None:
            # We don't know which div ended without tracking depth; rely on next module starting
            # to close out. Push module when we've seen path + table at least once and the row buf is empty.
            # We'll instead finalize when we see the closing of the module via a sentinel below.
            pass

    def handle_data(self, data):
        if self._in_h3:
            self._h3_buf.append(data)
        if self._in_h2:
            self._h2_buf.append(data)
        if self._in_a:
            self._a_text_buf.append(data)
        elif self._in_td or self._in_th:
            self._cell_buf.append(data)

    # ---- row classification --------------------------------------------
    def _finish_row(self):
        cells = self._row_cells
        self._row_cells = []

        if not cells or self.cur is None:
            return

        is_meta = self._row_class == "meta"

        # Title row: single th with colspan=3 (we lose the colspan attr in this parser
        # since we don't store it, but title rows are the FIRST meta row with just one th).
        if is_meta and len(cells) == 1 and cells[0]["kind"] == "th":
            if self.cur.get("title") is None:
                self.cur["title"] = cells[0]["text"]
            return

        # Meta "Allowed Methods" rows. Format varies:
        #   [th "Meta Information", th "Allowed Methods",       td "GET, ..."]
        #   [                       th "Allowed Methods (list)", td "GET"]
        #   [                       th "Allowed Methods (detail)", td "GET, PATCH"]
        if is_meta:
            label = None
            value = None
            for c in cells:
                t = c["text"]
                if c["kind"] == "th":
                    if t.startswith("Allowed Methods"):
                        label = t
                elif c["kind"] == "td":
                    value = t
            if label and value:
                self.cur["methods"].append((label, value))
            return

        # Header row: th th th  -> skip
        if all(c["kind"] == "th" for c in cells):
            return

        # Field row: td td td
        if len(cells) == 3 and all(c["kind"] == "td" for c in cells):
            name = cells[0]["text"]
            type_text = cells[1]["text"]
            type_link = cells[1]["link"]
            description = cells[2]["text"]
            self.cur["fields"].append(
                {
                    "name": name,
                    "type": type_text or (type_link or ""),
                    "type_link": type_link,
                    "description": description,
                }
            )
            return


def slugify(path: str) -> str:
    """Turn /api/admin/configuration/v1/conference/ into 'conference'.

    For embedded/response resources with longer paths, use the last meaningful segment(s).
    """
    parts = [p for p in path.strip("/").split("/") if p]
    return parts[-1] if parts else "unknown"


def section_for(path: str, section_name: str | None) -> str:
    if section_name and section_name in SECTIONS:
        return SECTIONS[section_name]
    # fallback by URL prefix
    if path.startswith("/api/admin/configuration/"):
        return "configuration"
    if path.startswith("/api/admin/status/"):
        return "status"
    if path.startswith("/api/admin/command/"):
        return "command"
    if path.startswith("/api/admin/history/"):
        return "history"
    if path.startswith("/embedded/"):
        return "embedded"
    if path.startswith("/response/"):
        return "responses"
    return "other"


def filename_for(path: str, section_dir: str) -> str:
    parts = [p for p in path.strip("/").split("/") if p]
    if section_dir in ("embedded", "responses") and len(parts) >= 2:
        # /embedded/upgrade_request/version_info/  -> upgrade_request__version_info.md
        return "__".join(parts[1:]) + ".md"
    # For sub-resources under /api/admin/<ns>/v1/<parent>/<id>/<child>/ keep parent+child
    # so we don't collide on e.g. media_stream.md.
    if section_dir in ("configuration", "status", "command", "history") and len(parts) > 5:
        tail = [p for p in parts[4:] if p != "<id>"]
        return "__".join(tail) + ".md"
    return slugify(path) + ".md"


def render_module(mod: dict) -> str:
    lines: list[str] = []
    title = mod.get("title") or ""
    path = mod["path"]

    lines.append(f"# {title}" if title else f"# {path}")
    lines.append("")
    lines.append(f"**Endpoint:** `{path}`")
    lines.append("")

    if mod["methods"]:
        lines.append("## Allowed methods")
        lines.append("")
        for label, value in mod["methods"]:
            lines.append(f"- **{label}:** {value}")
        lines.append("")

    if mod["fields"]:
        lines.append("## Fields")
        lines.append("")
        lines.append("| Field | Type | Description |")
        lines.append("|---|---|---|")
        for f in mod["fields"]:
            type_repr = f["type"].replace("|", "\\|")
            if f["type_link"]:
                # render as a markdown reference: type (-> linked-resource)
                type_repr = f"`{f['type_link']}` (related resource)"
            desc = f["description"].replace("|", "\\|").replace("\n", " ")
            name = f["name"].replace("|", "\\|")
            lines.append(f"| `{name}` | {type_repr} | {desc} |")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    if not HTML_PATH.exists():
        print(f"missing: {HTML_PATH}", file=sys.stderr)
        return 1

    html = HTML_PATH.read_text(encoding="utf-8")
    parser = SchemaParser()

    # Walk every <div class="module"> ... </div> by splitting on the marker.
    # Simpler than tracking div depth: feed each module's HTML to a fresh parser instance,
    # but we want a single 'section' state -> we'll just feed everything in one go.
    # However, our parser doesn't track when a module's div ends. We close on encountering
    # the next module start or section <h3> by flushing.
    #
    # Approach: split on '<div class="module">' to give us discrete chunks.
    # Each chunk is parsed standalone but we manually carry section across chunks.

    section = None
    modules: list[dict] = []

    # First find section markers and their offsets
    section_markers = [(m.start(), m.group(1)) for m in re.finditer(r"<h3>([^<]+)</h3>", html)]

    chunks = re.split(r'(<div class="module">)', html)
    # chunks alternates: prefix, '<div class="module">', body, '<div class="module">', body, ...
    cursor = 0
    for i, chunk in enumerate(chunks):
        if chunk == '<div class="module">':
            continue
        if i == 0:
            cursor += len(chunk)
            continue
        # find the most recent section header before this module's start
        module_start = sum(len(c) for c in chunks[: i - 1]) + len('<div class="module">') + (cursor if False else 0)
        # simpler: just scan h3s in chunk[0] cumulatively
        pass

    # That split approach got tangled. Easier: track section as we encounter <h3> headers
    # by streaming over the HTML directly with one parser. Use a custom subclass that
    # finalizes the current module when it sees the next <div class="module"> OR <h3>.

    class StreamingParser(SchemaParser):
        def handle_starttag(self, tag, attrs):
            attrs_d = dict(attrs)
            if tag == "div" and attrs_d.get("class") == "module" and self.cur is not None:
                # close out the previous module
                self.modules.append(self.cur)
                self.cur = None
            if tag == "h3" and self.cur is not None:
                self.modules.append(self.cur)
                self.cur = None
            super().handle_starttag(tag, attrs)

    sp = StreamingParser()
    sp.feed(html)
    if sp.cur is not None:
        sp.modules.append(sp.cur)

    if not sp.modules:
        print("no modules parsed", file=sys.stderr)
        return 2

    # Build output
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    index_entries: dict[str, list[tuple[str, str, str]]] = {}  # section -> [(path, title, filename)]

    for mod in sp.modules:
        if not mod["path"]:
            continue
        sec_dir = section_for(mod["path"], mod["section"])
        out_dir = OUT_DIR / sec_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        fname = filename_for(mod["path"], sec_dir)
        (out_dir / fname).write_text(render_module(mod), encoding="utf-8")
        index_entries.setdefault(sec_dir, []).append((mod["path"], mod.get("title") or "", fname))

    # INDEX.md
    section_order = ["configuration", "status", "command", "history", "embedded", "responses", "other"]
    section_titles = {
        "configuration": "Configuration  (`/api/admin/configuration/v1/`)",
        "status": "Status  (`/api/admin/status/v1/`)",
        "command": "Command  (`/api/admin/command/v1/`)",
        "history": "History  (`/api/admin/history/v1/`)",
        "embedded": "Embedded resources",
        "responses": "Responses",
        "other": "Other",
    }

    idx_lines = [
        "# Pexip Infinity Management API — schema index",
        "",
        "Generated from `API Schemas _ Pexip Infinity.html` (the rendered `/admin/platform/schema/` page).",
        "Each row links to a per-resource markdown file with the full field list and allowed methods.",
        "",
    ]
    total = 0
    for sec in section_order:
        if sec not in index_entries:
            continue
        entries = sorted(index_entries[sec], key=lambda e: e[0])
        total += len(entries)
        idx_lines.append(f"## {section_titles[sec]}  ({len(entries)})")
        idx_lines.append("")
        for path, title, fname in entries:
            rel = f"{sec}/{fname}"
            idx_lines.append(f"- [`{path}`]({rel}) — {title}")
        idx_lines.append("")

    idx_lines.append(f"_Total resources: **{total}**_")
    (OUT_DIR / "INDEX.md").write_text("\n".join(idx_lines) + "\n", encoding="utf-8")

    print(f"wrote {total} resources to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
