---
# Required: must match the folder name, use kebab-case.
name: skill-name

# Required: one sentence telling Claude when to invoke this skill.
# Include trigger keywords the user might say. Keep under ~200 chars.
description: Use when <situation>; produces <output>. Triggers on phrases like "<example>".

# Optional: restrict which tools the skill may call.
# allowed-tools: [Read, Grep, Glob, Bash]

# Optional: semver for the skill body.
# version: 0.1.0
---

# <Skill Title>

## When to use this skill

- Bullet the concrete triggering scenarios.
- Include shapes of user requests that should activate it.

## When NOT to use

- List out-of-scope situations so Claude doesn't over-trigger.

## Workflow

1. First step — be explicit about what to check or gather.
2. Second step — the core action.
3. Third step — verification or handoff.

## Examples

### Example 1 — <scenario>

User says: "..."

Expected behavior:
- ...

### Example 2 — <scenario>

...

## Red flags

Situations where the skill should pause and ask instead of proceeding:

- ...
