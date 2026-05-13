#!/usr/bin/env bash
# package.sh — build .skill (zip) packages for every skill in the repo.
#
# Output: dist/<skill-name>.skill
#
# .skill files are zip archives containing the SKILL.md and any referenced
# resources. They can be uploaded to Claude.ai (Pro / Max / Team / Enterprise).
#
# Usage:
#   ./scripts/package.sh                  # package every skill
#   ./scripts/package.sh <skill-name>     # package just one

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_SRC="$REPO_DIR/skills"
DIST_DIR="$REPO_DIR/dist"

mkdir -p "$DIST_DIR"

package_one() {
    local skill_path="$1"
    local name
    name="$(basename "$skill_path")"

    if [[ ! -f "$skill_path/SKILL.md" ]]; then
        echo "  ⚠️  Skipping $name (no SKILL.md)"
        return
    fi

    local out="$DIST_DIR/${name}.skill"
    rm -f "$out"

    # Build the zip with the skill folder at the root, so the archive contains
    # <skill-name>/SKILL.md (matching the format produced by Anthropic's
    # package_skill.py).
    (
        cd "$SKILLS_SRC"
        zip -qr "$out" "$name" \
            -x "*.DS_Store" \
            -x "*/__pycache__/*" \
            -x "*/.git/*" \
            -x "*/node_modules/*"
    )

    local size
    size=$(du -h "$out" | cut -f1)
    echo "  📦 $name → ${out#$REPO_DIR/} ($size)"
}

if ! command -v zip >/dev/null 2>&1; then
    echo "Error: 'zip' command not found. Install zip and retry." >&2
    exit 1
fi

if [[ $# -ge 1 ]]; then
    target="$SKILLS_SRC/$1"
    if [[ ! -d "$target" ]]; then
        echo "Skill not found: $1" >&2
        exit 1
    fi
    package_one "$target"
else
    echo "Packaging all skills → $DIST_DIR"
    echo
    for skill_path in "$SKILLS_SRC"/*/; do
        [[ -d "$skill_path" ]] || continue
        package_one "$skill_path"
    done
fi

echo
echo "Done. Built packages:"
ls -1 "$DIST_DIR" | sed 's/^/  - /'
