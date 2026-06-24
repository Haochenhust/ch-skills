# Business Logic

The Logic layer answers three questions in order: **how does it make money, why can it keep making money, and who is trying to take it away.** Numbers carry this layer. Adjectives do not.

Framing borrows from 段永平 ("道") — the qualitative essence of a business — and 《投资至简》 ("术") — the procedural checks. Both together.

## Part 1 — 商业模式 (how money flows)

Spell out the revenue equation in one sentence before anything else. Examples:

- **拼多多**: GMV × take rate (ads + commission) − user subsidies − traffic cost.
- **Anthropic**: API tokens billed × price per token − compute cost − research compensation − safety/ops overhead.
- **Costco**: membership fees (~70% of operating profit) + thin-margin merchandise (~10-11%).

Then decompose each factor:

1. **Customer** — who pays, how they found the product, how much they cost to acquire (CAC if available).
2. **Price** — unit price, pricing mechanism (ad auction / subscription / per-seat / usage). What pricing power exists?
3. **Frequency / duration** — daily? annual? 10-year enterprise contract?
4. **Expansion** — does revenue per customer grow over time (NDR for SaaS, ARPU trend)?

If the user is on a Scenario B/C/D profile, also touch:

- **Unit economics** — LTV/CAC, payback period, contribution margin.
- **Cost structure** — fixed vs variable, COGS composition. What scales and what doesn't?
- **Working capital** — does the business run on customer prepayments (good) or extend customer credit (dangerous)?

Aim for at least 3 specific numbers in this subsection. Directional claims ("high margin", "sticky revenue") are not good enough alone.

## Part 2 — 生意属性 (what kind of business is this)

Adapted from 《投资至简》. Ask:

1. **Is this a good business?** — structural gross margin, capital intensity, cyclicality, regulatory overhang.
2. **Is demand durable?** — or is it a fashion / platform-shift victim waiting to happen?
3. **Does scale help or hurt?** — some businesses scale linearly (consulting), some exponentially (software), some compress margins (airlines).
4. **What breaks it?** — name the top 2–3 things that would turn this into a bad business in 3 years.

Call the business-type bluntly: "This is a low-margin, capital-intensive retail business with a marginal loyalty moat" is better than "This is a consumer company."

## Part 3 — 管理层 & 企业文化 (the people behind the numbers)

From 段永平's "本分" framing:

- Does management keep promises to customers, employees, and shareholders?
- Are they operators who understand the business, or deal-makers in love with M&A?
- Capital allocation history — share buybacks at sane prices? Acquisitions that worked? Dividends with discipline?
- Stock-based compensation — is dilution subsidizing the story?
- Governance — any red flags (related-party transactions, auditor changes, VIE structure complexity, concentrated founder control without accountability)?

This is judgment-heavy. Cite behavior ("in 2019 they returned $X via buyback at $Y share price, in hindsight a good/bad call") rather than pronouncements.

## Part 4 — 竞争格局 (per 卡兹克 branching)

Follow scenario branching based on competitive density:

- **No direct competitors** — ask *why*. Usually one of: market too small, regulatory moat, tech frontier, or you're defining the category wrong.
- **1–2 serious competitors** — do a direct comparison: product, go-to-market, balance sheet, trajectory. Declare who's winning and why.
- **3+ competitors** — pick 3–5 representative ones (market leader, fast-follower, insurgent, declining incumbent). Do a lightweight comparison, not a matrix.

Avoid Porter's Five Forces as a literal template. Use the thinking (substitutes, buyer/supplier power, new entrants) as *questions* you answer in prose.

## How Logic feeds Story and Judgment

- **Back to Story**: if the Logic layer reveals the real moat is switching costs in legacy enterprise contracts, the founder-myth story needs to account for how they ended up there — was it a deliberate go-to-market choice or a lucky side-effect?
- **Forward to Judgment**: the Logic section should surface at least 2 quantifiable bets that the company's future depends on. These become the Judgment layer's targets to defend or attack.

## Checklist before handing off

- [ ] Revenue equation stated in one sentence.
- [ ] At least 3 specific numbers with sources.
- [ ] A concrete claim about the moat type (cross-ref `moat-types.md`).
- [ ] A named assessment of management (not "strong team").
- [ ] A named winner in the competitive landscape if it's a contested market.
