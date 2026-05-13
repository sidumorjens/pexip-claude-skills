# Contributing

Thanks for considering a contribution. The bar for adding to this repo is that the skill should make Claude **noticeably better** at a specific Pexip task — better than it would do from training data and live web search alone.

## Adding a new skill

### 1. Decide what the skill is for

A good skill has:

- A **bounded scope** — "Pexip External Policy" is good. "All things Pexip" is too broad.
- A **specific trigger condition** — what user intent should activate it?
- **Reusable content** — things that come up across many conversations, not a one-off answer.
- **Hard-won knowledge** — gotchas, version-specific behaviour, conventions, things not obvious from the docs.

If you find yourself writing "general Pexip docs," stop — that's already on docs.pexip.com. The skill should be the implementation knowledge **around** the docs.

### 2. Copy the template

```bash
cp -r docs/skill-template skills/<your-skill-name>
```

Skill names should be:

- All lowercase
- Hyphen-separated
- Prefixed `pexip-` (or another clear scope) so they're identifiable in a long `available_skills` list
- Descriptive of the area, not the action ("pexip-management-api" not "use-pexip-mgmt-api")

### 3. Fill in `SKILL.md`

The YAML frontmatter is the most important part — it's how Claude decides whether to load the skill.

```yaml
---
name: pexip-your-skill
description: >
  One sentence on what this skill is. Then specific phrases and contexts that
  should trigger it: "Use this skill whenever the user is doing X, mentions Y,
  or asks about Z. Also triggers for ABC, DEF, and GHI."
---
```

Tips for writing a good `description`:

- Be **specific** about triggering phrases — Claude has a tendency to under-trigger
- List **multiple synonyms** for the same concept (e.g. "VMR" and "Virtual Meeting Room")
- Include **adjacent concepts** that should pull this skill in (e.g. external policy skill triggers on "ABAC", "breakout rooms", "Policy Studio")
- Mention **what the user might be doing**, not just the topic ("designing", "building", "debugging")

After the frontmatter, the body should:

- Open with a one-paragraph overview
- Use a **quick decision tree** at the top if there are many sub-topics (route to references/)
- Cover the practical patterns, gotchas, and conventions
- Stay under ~500 lines (the validator warns at 600); move detail into `references/`

### 4. Add reference files (optional)

For larger skills, put detailed content in `references/<topic>.md` and link to them from SKILL.md:

```markdown
For all service_configuration response fields, see `references/service-configuration.md`.
```

References load on demand — they don't bloat the always-in-context skill metadata, but Claude can pull them when needed.

### 5. Validate

```bash
./scripts/validate.sh
```

This checks frontmatter, naming, and that referenced files exist. All checks must pass.

### 6. Test locally

Install the skill into your own Claude Code:

```bash
./scripts/install-one.sh <your-skill-name> --symlink
```

Then in Claude Code, ask realistic questions that should trigger the skill. Watch whether:

- Claude actually consults the skill (it should appear in `available_skills` and behave differently from the baseline)
- The advice is accurate and useful
- The references load when expected
- Edge cases produce sensible answers

Iterate. A skill that's *technically correct but doesn't trigger* is worse than no skill at all.

### 7. Open a PR

In the PR description:

- What does this skill do?
- When should it trigger?
- What sources / experience is this distilled from?
- How did you test it?

## Updating an existing skill

Same workflow: edit, validate, test locally, PR. Try to keep the `name` in the frontmatter and folder name stable across versions — changing them is a breaking change for anyone who has installed it.

If a Pexip version bump (e.g. v39 → v40) changes documented behaviour, note the version when adding new fields:

```markdown
| `new_field` | Boolean | `false` | Description. *(Pexip v40+)* |
```

## Style conventions

- Use British English where it's natural; American is also fine. Pick one per skill and stick to it.
- Prefer **prose with tables** over **deeply nested bullet lists**. Tables read better when scanning for a specific field.
- Code samples should be **runnable** — not pseudocode. If a snippet needs imports, include them.
- Cite the Pexip docs page when documenting a specific feature, so reviewers can verify.
- Keep examples **concrete** — use real-looking alias formats (`meet.alice@example.com`), real-looking UUIDs, real Pexip behaviours.

## What not to add

- General LLM coding advice — out of scope
- Marketing or sales material — out of scope
- Customer-specific configuration — keep these in customer-specific private repos
- Credentials, real IP addresses, real customer names — never commit these

## Questions?

Open an issue. If you're not sure whether something is a good skill candidate, file an issue to discuss before doing the work.
