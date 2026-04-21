# Contributing

Thanks for considering a contribution. This repo is a curated collection of Claude Code skills, so the bar is *clarity and correctness*, not feature count.

## Adding a new skill

1. **Create the directory** — one skill per folder under `skills/`. The folder name should match the skill's `name` field, using `kebab-case`:

   ```
   skills/<skill-name>/SKILL.md
   ```

2. **Start from the template** — copy `skills/_template/SKILL.md` into the new folder and edit.

3. **Fill in the frontmatter** — at minimum:

   ```yaml
   ---
   name: <skill-name>              # Must match folder name
   description: <one sentence>     # When should Claude use this skill?
   ---
   ```

   Optional fields:

   - `allowed-tools: [Read, Grep, Bash]` — restrict which tools the skill may use.
   - `version: 0.1.0` — semver if you want explicit versioning.

4. **Write the body** — the skill body is loaded only when triggered, so be generous with:

   - **When to use / when not to use** — helps Claude make the trigger decision.
   - **Step-by-step workflow** — numbered or checklisted.
   - **Examples** — real input/output, not placeholders.
   - **Red flags** — common mistakes the skill should prevent.

## Description guidance

The `description` is the primary signal Claude uses to decide whether to load the skill. Treat it like a doc string:

- Say **what kind of task** triggers it, not just what it does.
- Include **keywords** a user would naturally say (`"refactor"`, `"lint"`, `"migrate"`).
- Keep it under ~200 characters.

Bad: `Refactors code.`
Good: `Use when refactoring a function to extract helpers, rename symbols, or split a long method — produces a plan before editing.`

## Testing your skill

Before opening a PR:

1. Symlink it into your local `~/.claude/skills/` and restart Claude Code.
2. Phrase a realistic request and check whether the skill triggers.
3. Walk through the workflow end to end — does the body give Claude enough to succeed?
4. Try an adversarial phrasing (vague, off-topic) — does it correctly *not* trigger?

## Pull requests

- One skill per PR keeps review simple.
- Include a short PR description: what problem the skill solves, and one example invocation.
- Commit messages: `feat(skills): add <skill-name>` or `fix(skills/<name>): <what>`.
