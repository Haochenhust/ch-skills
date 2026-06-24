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
| [`industry-chain-research`](skills/industry-chain-research/) | 产业链研究：从宏观趋势拆解产业链、定位瓶颈环节、找到具体标的、交叉验证风险。在结构化框架里让 AI 做产业链研究员。Invoked by 产业链分析 / 拆产业链 / 瓶颈分析 / 景气度投资 / "帮我拆一下XX产业链". |
| [`intrinsic-value-analysis`](skills/intrinsic-value-analysis/) | 用老唐（唐朝）估值法分析企业内在价值。以巴菲特/格雷厄姆 DCF 思想的工程化简化为骨架：三大前提排雷 → 把好公司当债券 → 三年后合理估值打五折买入。Invoked by 估值 / 内在价值 / "现在能不能买" / "什么价位卖". |
| [`company-analyzer`](skills/company-analyzer/) | Analyze a company through three layers — story, logic, judgment — and deliver a narrative-driven report with a clear take. Invoked by "研究 XX 公司" / "深度分析 XX" / "带我看懂 XX 这家公司" or naming a company alongside investment/career/competition context. |

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
    ├── marxist-method-for-action/   # Decision-analysis methodology
    │   ├── SKILL.md
    │   ├── references/
    │   ├── scripts/
    │   └── evals/
    ├── industry-chain-research/     # Industry chain research
    │   ├── SKILL.md
    │   └── REFERENCE.md
    ├── intrinsic-value-analysis/    # Intrinsic value analysis
    │   └── SKILL.md
    └── company-analyzer/            # Company deep analysis
        ├── SKILL.md
        ├── references/
        └── templates/
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
