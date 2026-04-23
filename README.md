# ch-skills

Open-source skills — shareable & installable.

A personal collection of [Claude Code](https://docs.claude.com/en/docs/claude-code) skills. Each skill is a self-contained directory with a `SKILL.md` manifest plus any supporting files, ready to drop into your own Claude Code setup.

## What is a skill?

A skill is a named capability that Claude Code can discover and invoke on demand. Each skill lives in its own folder and declares itself via YAML frontmatter in `SKILL.md`:

```markdown
---
name: my-skill
description: One sentence telling Claude when to use this skill.
---

Body content — instructions, workflow, examples.
```

Claude reads the frontmatter at session start and loads the full body only when the skill is triggered.

## Skills in this repo

| Skill | Purpose |
|---|---|
| [`meta-prompt`](skills/meta-prompt/) | Turn a vague, conversational task into a high-quality, copy-pastable prompt for another AI (Claude or GPT). Invoked by saying "help me write a prompt", "optimize this for Claude/GPT", or `/mp`. |
| [`marxist-method-for-action`](skills/marxist-method-for-action/) | Rigorous problem-analysis methodology for substantive decisions (housing, career, medical, investment, tech/architecture, debugging, …). Six base principles plus nine Mao-style operational hooks (investigation circle, stakeholder mapping, main-contradiction transition, staged strategy, worst-case wargaming, concentrated main attack, active levers, typical-case deep-dive). Invoked by `/mma` or phrases like 用马哲分析 / 用毛选方法 / 矛盾分析一下 / 实事求是地看. |

## Repository layout

```
ch-skills/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
└── skills/
    ├── meta-prompt/                 # Prompt optimizer
    │   ├── SKILL.md
    │   ├── references/
    │   │   └── techniques.md
    │   └── evals/
    │       └── evals.json
    └── marxist-method-for-action/   # Decision-analysis methodology
        ├── SKILL.md
        ├── references/
        │   ├── mao-playbook.md
        │   ├── domain-examples.md
        │   └── before-after-case-studies.md
        ├── scripts/
        │   └── context_questions.py
        └── evals/
            └── evals.json
```

## Installation

Pick whichever fits your workflow:

**Option A — install a single skill**

```bash
git clone https://github.com/Haochenhust/ch-skills.git /tmp/ch-skills
cp -r /tmp/ch-skills/skills/meta-prompt ~/.claude/skills/
```

**Option B — symlink the whole collection**

```bash
git clone https://github.com/Haochenhust/ch-skills.git ~/code/ch-skills
ln -s ~/code/ch-skills/skills/meta-prompt ~/.claude/skills/meta-prompt
```

**Option C — track upstream and pull updates**

```bash
git clone https://github.com/Haochenhust/ch-skills.git ~/.claude/skills-ch
# Then symlink individual skills as needed.
```

After installing, restart Claude Code (or start a new session) so the new skill is picked up.

## Contributing

New skills are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for the directory and frontmatter conventions.

## License

Released under the [MIT License](LICENSE).
