---
name: hello-world
description: Minimal example skill that greets the user and demonstrates the SKILL.md structure. Use when the user asks for a "hello world skill demo" or wants to verify that skill loading works.
version: 0.1.0
---

# Hello World

A tiny skill that exists so you can verify your Claude Code setup picks up skills from this repo.

## When to use this skill

- The user says "run the hello-world skill" or "test my skills setup".
- You need a sanity check that a freshly installed skill is being discovered and invoked.

## When NOT to use

- Any real task. This skill does nothing useful beyond demonstrating the format.

## Workflow

1. Acknowledge that the hello-world skill was triggered.
2. Print a short greeting that includes the current date (so the user sees the skill body actually executed, not a cached response).
3. Point the user at `skills/_template/SKILL.md` if they want to create their own skill next.

## Example

User: "Run the hello-world skill."

Response:

> Hello from the `hello-world` skill — loaded from the ch-skills repo.
> Next step: copy `skills/_template/SKILL.md` into a new folder under `skills/` and start editing.
