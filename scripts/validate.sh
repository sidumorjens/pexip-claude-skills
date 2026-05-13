#!/usr/bin/env bash
# validate.sh — sanity-check every skill in the repo.
#
# Checks performed per skill:
#   1. SKILL.md exists
#   2. SKILL.md has YAML frontmatter with `name` and `description`
#   3. `name` in frontmatter matches the folder name
#   4. SKILL.md is not absurdly long (warn > 600 lines)
#   5. Any `references/*.md` paths mentioned in SKILL.md actually exist
#
# Exit code: 0 if all skills valid, 1 if any errors.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_SRC="$REPO_DIR/skills"

errors=0
warnings=0

validate_skill() {
    local skill_path="$1"
    local name
    name="$(basename "$skill_path")"

    echo "🔍 $name"

    local skill_md="$skill_path/SKILL.md"
    if [[ ! -f "$skill_md" ]]; then
        echo "    ❌ Missing SKILL.md"
        errors=$((errors + 1))
        return
    fi

    # Check for frontmatter
    if ! head -n 1 "$skill_md" | grep -q '^---$'; then
        echo "    ❌ SKILL.md does not start with YAML frontmatter (--- on line 1)"
        errors=$((errors + 1))
        return
    fi

    # Extract frontmatter (between first two --- lines)
    local frontmatter
    frontmatter="$(awk '/^---$/{c++; if(c==2) exit; next} c==1' "$skill_md")"

    # Check name field
    local fm_name
    fm_name="$(printf '%s\n' "$frontmatter" | grep -E '^name:' | head -n 1 | sed 's/^name:[[:space:]]*//' | tr -d '"' | tr -d "'")"
    if [[ -z "$fm_name" ]]; then
        echo "    ❌ Missing 'name' in frontmatter"
        errors=$((errors + 1))
    elif [[ "$fm_name" != "$name" ]]; then
        echo "    ❌ Frontmatter name '$fm_name' does not match folder name '$name'"
        errors=$((errors + 1))
    fi

    # Check description field (may be multi-line, but must be present)
    if ! printf '%s\n' "$frontmatter" | grep -qE '^description:'; then
        echo "    ❌ Missing 'description' in frontmatter"
        errors=$((errors + 1))
    fi

    # Length warning
    local lines
    lines=$(wc -l < "$skill_md")
    if [[ $lines -gt 600 ]]; then
        echo "    ⚠️  SKILL.md is $lines lines (consider moving content to references/)"
        warnings=$((warnings + 1))
    fi

    # Check referenced files in references/
    if [[ -d "$skill_path/references" ]]; then
        # Extract all references/<name>.md mentions from SKILL.md
        while IFS= read -r ref; do
            local ref_path="$skill_path/$ref"
            if [[ ! -f "$ref_path" ]]; then
                echo "    ❌ Referenced file not found: $ref"
                errors=$((errors + 1))
            fi
        done < <(grep -oE 'references/[a-zA-Z0-9._-]+\.md' "$skill_md" | sort -u)
    fi

    echo "    ✓ ok ($lines lines)"
}

if [[ ! -d "$SKILLS_SRC" ]]; then
    echo "No skills/ directory found at $SKILLS_SRC" >&2
    exit 1
fi

for skill_path in "$SKILLS_SRC"/*/; do
    [[ -d "$skill_path" ]] || continue
    validate_skill "$skill_path"
done

echo
echo "Summary: $errors error(s), $warnings warning(s)"

if [[ $errors -gt 0 ]]; then
    exit 1
fi
