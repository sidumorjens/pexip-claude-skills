#!/usr/bin/env bash
# install.sh — install every skill under skills/ to your Claude skills directory.
#
# Usage:
#   ./scripts/install.sh
#   CLAUDE_SKILLS_DIR=/custom/path ./scripts/install.sh
#   ./scripts/install.sh --symlink         # symlink instead of copy (active dev)
#   ./scripts/install.sh --project         # install into ./.claude/skills/ instead of $HOME
#
# Default destination: ~/.claude/skills/

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_SRC="$REPO_DIR/skills"

USE_SYMLINK=0
PROJECT_INSTALL=0

for arg in "$@"; do
    case "$arg" in
        --symlink|-s) USE_SYMLINK=1 ;;
        --project|-p) PROJECT_INSTALL=1 ;;
        --help|-h)
            head -n 11 "$0" | tail -n 10 | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        *) echo "Unknown argument: $arg" >&2; exit 1 ;;
    esac
done

if [[ $PROJECT_INSTALL -eq 1 ]]; then
    DEST_DIR="$(pwd)/.claude/skills"
else
    DEST_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
fi

mkdir -p "$DEST_DIR"

echo "Installing skills from: $SKILLS_SRC"
echo "                    to: $DEST_DIR"
if [[ $USE_SYMLINK -eq 1 ]]; then
    echo "                  mode: symlink"
else
    echo "                  mode: copy"
fi
echo

if [[ ! -d "$SKILLS_SRC" ]] || [[ -z "$(ls -A "$SKILLS_SRC" 2>/dev/null)" ]]; then
    echo "No skills found in $SKILLS_SRC" >&2
    exit 1
fi

count=0
for skill_path in "$SKILLS_SRC"/*/; do
    [[ -d "$skill_path" ]] || continue
    name="$(basename "$skill_path")"
    target="$DEST_DIR/$name"

    if [[ ! -f "$skill_path/SKILL.md" ]]; then
        echo "  ⚠️  Skipping $name (no SKILL.md)"
        continue
    fi

    # Remove any existing install
    if [[ -e "$target" ]] || [[ -L "$target" ]]; then
        rm -rf "$target"
    fi

    if [[ $USE_SYMLINK -eq 1 ]]; then
        ln -s "$skill_path" "$target"
        echo "  🔗 $name (symlinked)"
    else
        cp -r "$skill_path" "$target"
        echo "  ✅ $name (copied)"
    fi
    count=$((count + 1))
done

echo
echo "Installed $count skill(s) to $DEST_DIR"
echo
echo "Installed skills:"
ls "$DEST_DIR" | sed 's/^/  - /'
