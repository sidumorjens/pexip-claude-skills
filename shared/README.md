# Shared Resources

This folder is for cross-skill reference material that multiple skills might
want to reference — for example, a Pexip version compatibility matrix, shared
glossaries, or common API conventions.

Note: Claude's skill loader treats each skill folder as isolated; it doesn't
automatically pull files from `shared/` into a skill's context. If you want a
skill to actually use shared content, copy or symlink the file into that skill's
`references/` directory at install time (or just reference it via documentation
links).

## When to put something here

- Reference material that legitimately applies to 3+ skills
- Things that change rarely (a version matrix, a standard glossary)
- Documentation aimed at human contributors, not Claude

## When NOT to put something here

- Anything a single skill is the primary user of — that lives in the skill's
  own `references/` directory
- Anything Claude needs to load automatically — skills don't auto-load shared
  files
