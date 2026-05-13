---
name: pexip-skill-template
description: >
  REPLACE THIS — one sentence describing what the skill does. Then specific
  trigger phrases: "Use this skill whenever the user is working with X, mentions
  Y, asks about Z, or needs to do ABC. Also triggers for DEF, GHI, JKL." Be
  specific and a little pushy — Claude tends to under-trigger skills, so list
  multiple synonyms and adjacent concepts that should pull this in.
---

# Pexip <Topic> — Expert Skill

One-paragraph overview: what this skill helps with and what kind of background
it's distilled from. This sets the frame for the rest of the file.

---

## Quick Decision Tree

| Goal | Read this first |
|---|---|
| Task A | `references/topic-a.md` |
| Task B | `references/topic-b.md` |
| Debug a problem | §N below |

(Drop this section if the skill is small enough that a single SKILL.md covers everything.)

---

## 1. Background / Concepts

What does someone need to know up-front to use this skill effectively? Keep it
short — link to docs.pexip.com for the canonical reference and focus on the
parts that aren't in the docs (gotchas, conventions, version differences).

---

## 2. The Main Pattern

The most important thing the skill teaches. Use prose and tables. Worked code
examples should be runnable.

```python
# Example
```

---

## 3. Gotchas

Things that bit you (or someone) in production, that aren't documented anywhere
obvious.

| Symptom | Likely cause |
|---|---|
| ... | ... |

---

## 4. Checklist

- [ ] Thing to remember
- [ ] Thing to remember
- [ ] Thing to remember
