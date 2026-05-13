# Pexip Claude Skills

A collection of [Claude Agent Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) for working with [Pexip Infinity](https://www.pexip.com/) and the wider Pexip platform. Each skill captures hard-won, field-tested knowledge that makes Claude meaningfully better at a specific Pexip task — without you having to re-explain context every conversation.

## What's in here

| Skill | Purpose |
|---|---|
| [`pexip-external-policy`](skills/pexip-external-policy/) | Designing and implementing Pexip Infinity External Policy servers and local Jinja2 policy scripts. Covers all six request types, ABAC patterns, breakout rooms, and common gotchas. |
| _(more to come)_ | |

## What is a Claude Skill?

A skill is a folder containing a `SKILL.md` (with YAML frontmatter describing when to trigger it) plus optional reference files and scripts. Claude consults relevant skills automatically based on the conversation. Skills work with:

- **Claude Code** (CLI) — drop the skill into `~/.claude/skills/<skill-name>/` or `<project>/.claude/skills/<skill-name>/`
- **Claude.ai apps** (Pro/Max/Team/Enterprise) — upload a packaged `.skill` file via Settings → Capabilities → Skills
- **Claude API / Agent SDK** — load via the code execution tool

The format is plain markdown plus YAML frontmatter — portable, reviewable, and version-controllable.

## Installation

### Install all skills (recommended)

Clone the repo and run the install script:

```bash
git clone https://github.com/lorist/pexip-claude-skills.git
cd pexip-claude-skills
./scripts/install.sh
```

This copies every skill in `skills/` to `~/.claude/skills/`, making them available in Claude Code immediately. Override the destination with `CLAUDE_SKILLS_DIR=/custom/path ./scripts/install.sh`.

### Install a single skill

```bash
./scripts/install-one.sh pexip-external-policy
```

### Install for Claude.ai (web/desktop)

Build packaged `.skill` files and upload them via the Claude.ai settings:

```bash
./scripts/package.sh                # outputs dist/<skill-name>.skill for every skill
```

Then in Claude.ai: **Settings → Capabilities → Skills → Upload skill** and pick the `.skill` file. (Available on Pro / Max / Team / Enterprise plans.)

### Manual install (no script)

A skill is just a folder. Copy it into your skills directory:

```bash
cp -r skills/pexip-external-policy ~/.claude/skills/
```

Or, for active development against a single machine, symlink it:

```bash
ln -s "$(pwd)/skills/pexip-external-policy" ~/.claude/skills/pexip-external-policy
```

Symlinking means `git pull` instantly updates the installed skill.

## Verifying

In Claude Code, ask something that should trigger one of the skills:

> "Help me draft an external policy server response for a Pexip breakout room."

Claude should consult the relevant SKILL.md and respond with field-accurate, context-aware guidance.

## Contributing a new skill

See [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md). Short version: copy `docs/skill-template/` into `skills/<your-skill-name>/`, fill in the SKILL.md and any references, and run `./scripts/validate.sh` before opening a PR.

## Versioning

This repo uses single-tag semantic versioning across all skills. Tagged releases (`v1.0.0`, `v1.1.0`, …) on GitHub include built `.skill` files as release assets for easy distribution to non-developers.

## Licence

See [`LICENSE`](LICENSE).

## Acknowledgements

These skills are distilled from real-world Pexip deployments — production policy servers, ABAC enforcement, Webapp3 plugins, partner integrations, and a lot of trial and error. If you find a gap, please open an issue or PR.
