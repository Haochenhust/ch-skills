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
| [`wechat-feeds`](skills/wechat-feeds/) | Maintain a local, incrementally-updated library of WeChat Official Account (公众号) articles as Markdown + a SQLite index, and pull new posts on demand. Bundles a self-contained Bun scraper that drives a logged-in Chrome via a tiny CDP proxy. Invoked by "update my feeds" / "拉一下公众号" / "增量更新公众号文章". |

### A-share investment research toolkit

A set of composable skills for A-share (A股) stock research. Analysis skills call the data skills; set your own `TUSHARE_TOKEN` (no credentials are bundled).

| Skill | Purpose |
|---|---|
| [`stock-analyzer`](skills/stock-analyzer/) | Deep-dive individual stock analysis across 5 dimensions (business, financials, valuation, catalysts, risks) → structured research note with a clear buy/sell/hold thesis and falsification conditions. Invoked by "分析一下XX股票" / "这只股票能不能买". |
| [`technical-analyzer`](skills/technical-analyzer/) | Secondary timing tool — MA trend, support/resistance, volume analysis for entry/exit. Never the primary basis. Invoked by "现在能买吗" / "技术面怎么样" / "支撑位在哪". |
| [`valuation-calculator`](skills/valuation-calculator/) | Relative valuation: PE/PB/PS historical percentiles, peer-comparison tables, PE/PB-based target prices. Distinct from the DCF-style [`intrinsic-value-analysis`](skills/intrinsic-value-analysis/). Invoked by "这只股票贵不贵" / "目标价多少". |
| [`industry-chain-mapper`](skills/industry-chain-mapper/) | Build & maintain persistent industry-chain map artifacts (upstream/mid/down, key companies, market share, elasticity ranking). Artifact-focused complement to [`industry-chain-research`](skills/industry-chain-research/). Invoked by "梳理一下XX产业链". |
| [`catalyst-tracker`](skills/catalyst-tracker/) | Forward-looking catalyst calendar (earnings, conferences, policy events) linked to tracked stocks. Invoked by "最近有什么催化剂" / "财报什么时候出". |
| [`news-scanner`](skills/news-scanner/) | Scan Xueqiu / Eastmoney / 10jqka + web search for investment news by tracked keywords; reports HIGH/MEDIUM signal only. Invoked by "最近有什么新消息" / "扫描一下XX的最新动态". |
| [`tushare-data`](skills/tushare-data/) | Primary structured A-share data via Tushare Pro — OHLCV, valuation, financial statements, shareholders, forecasts. CLI over the tushare SDK. Requires your own `TUSHARE_TOKEN`. |
| [`stock-market-data`](skills/stock-market-data/) | Free A-share/US market data via AKShare — trading-day checks, index/sector/limit-up-pool/northbound, per-stock daily OHLCV. No token needed. |
| [`financial-data-fetcher`](skills/financial-data-fetcher/) | Financial statements + ETF data (Tushare primary, AKShare fallback/ETFs). Orchestrates the two data skills above. |

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
    ├── company-analyzer/            # Company deep analysis
    │   ├── SKILL.md
    │   ├── references/
    │   └── templates/
    ├── wechat-feeds/                # WeChat 公众号 feed library + updater
    │   ├── SKILL.md
    │   └── tool/                    # self-contained Bun scraper + bundled CDP proxy
    │
    ├── stock-analyzer/              # ┐ A-share investment research toolkit
    ├── technical-analyzer/          # │  (analysis skills call the data skills)
    ├── valuation-calculator/        # │
    ├── industry-chain-mapper/       # │
    ├── catalyst-tracker/            # │
    ├── news-scanner/                # │
    ├── tushare-data/                # │  Tushare Pro CLI    (SKILL.md + scripts/)
    ├── stock-market-data/           # │  AKShare CLI        (SKILL.md + scripts/)
    └── financial-data-fetcher/      # ┘  financials + ETFs  (SKILL.md)
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
