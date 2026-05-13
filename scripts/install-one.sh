#!/usr/bin/env bash
# install-one.sh — install a single skill by name.
#
# Usage:
#   ./scripts/install-one.sh <skill-name>
#   ./scripts/install-one.sh pexip-external-policy --symlink

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_SRC="$REPO_DIR/skills"

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <skill-name> [--symlink] [--project]" >&2
    echo
    echo "Available skills:" >&2
    ls "$SKILLS_SRC" 2>/dev/null | sed 's/^/  - /' >&2
    exit 1
fi

SKILL_NAME="$1"
shift

USE_SYMLINK=0
PROJECT_INSTALL=0
for arg in "$@"; do
    case "$arg" in
        --symlink|-s) USE_SYMLINK=1 ;;
        --project|-p) PROJECT_INSTALL=1 ;;
        *) echo "Unknown argument: $arg" >&2; exit 1 ;;
    esac
done

SKILL_PATH="$SKILLS_SRC/$SKILL_NAME"

if [[ ! -d "$SKILL_PATH" ]] || [[ ! -f "$SKILL_PATH/SKILL.md" ]]; then
    echo "Skill not found or invalid: $SKILL_NAME" >&2
    echo "Available skills:" >&2
    ls "$SKILLS_SRC" 2>/dev/null | sed 's/^/  - /' >&2
    exit 1
fi

if [[ $PROJECT_INSTALL -eq 1 ]]; then
    DEST_DIR="$(pwd)/.claude/skills"
else
    DEST_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
fi

mkdir -p "$DEST_DIR"
TARGET="$DEST_DIR/$SKILL_NAME"

if [[ -e "$TARGET" ]] || [[ -L "$TARGET" ]]; then
    rm -rf "$TARGET"
fi

if [[ $USE_SYMLINK -eq 1 ]]; then
    ln -s "$SKILL_PATH" "$TARGET"
    echo "🔗 Installed $SKILL_NAME → $TARGET (symlinked)"
else
    cp -r "$SKILL_PATH" "$TARGET"
    echo "✅ Installed $SKILL_NAME → $TARGET"
fi
