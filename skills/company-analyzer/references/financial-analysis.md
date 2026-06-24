# Financial Analysis (Scenario D — Public Companies)

Only load this file if the company is publicly listed or has filed audited statements. For private startups, the Logic layer carries the numerical weight instead.

Goal: translate the financials into three or four claims that *support or contradict* the Story + Logic so far. Raw statement dumps are an anti-pattern.

## Four-pass reading

### Pass 1 — Quality of earnings

Look for the gap between reported profit and real cash:

- **Gross margin trend** over 5 years. Stable? Expanding? Compressing?
- **Operating margin** vs category peers. Best-in-class, middle of pack, or falling behind?
- **Free cash flow / net income ratio** over 3+ years. Persistent FCF < NI is a red flag (earnings management, rising working-capital drain, capex-heavy).
- **Revenue recognition aggressiveness** — any recent policy changes? Channel-stuffing signals (receivable growth >> revenue growth)?
- **Non-GAAP / adjusted EBITDA inflation** — how many add-backs? Is SBC treated as a "real" cost?

### Pass 2 — Capital efficiency

Does the business actually compound capital?

- **ROIC** — return on invested capital. Over the cycle, is it consistently > WACC?
- **ROE decomposition** (DuPont) — is ROE driven by margin, asset turnover, or leverage? Leverage-driven ROE is fragile.
- **Reinvestment runway** — how much capital can the company redeploy at these returns? Is it widening or shrinking?
- **Capital allocation history** — buybacks (at sane prices?), dividends, M&A (value-creating or destroying?).

### Pass 3 — Balance sheet and working capital

What happens if the environment turns?

- **Debt maturity ladder** — any refinancing wall in the next 24 months?
- **Net debt / EBITDA** vs covenant thresholds and peer levels.
- **Cash conversion cycle** — DSO + DIO − DPO. Improving or deteriorating? For retailers & manufacturers this is often more important than the P&L.
- **Hidden liabilities** — operating leases, pension underfunding, legal contingencies, VIE structure risk (for US-listed Chinese cos).

### Pass 4 — Segment & customer concentration

- Break the P&L into segments. Is one segment subsidizing another? Which one is actually the business?
- **Customer concentration** — top 10 customers as % of revenue. >30% is a yellow flag, >50% is a red flag.
- **Geographic concentration** — currency risk, regulatory risk.
- **Related-party transactions** — particularly for Chinese A-shares and certain family-controlled groups.

## What to deliver

A concise financial paragraph that takes a position on:

1. **Is reported profit real?** — quality of earnings verdict.
2. **Does the business compound?** — ROIC-vs-WACC verdict across the cycle.
3. **Can it survive a bad year?** — balance sheet stress test in one sentence.
4. **Where should I look next quarter?** — 1–2 specific line items that will confirm or break the thesis.

Do not paste the income statement. The reader can open 10-K themselves.

## Red flags that close the book

Call these out if seen; they often invalidate the Story + Logic entirely:

- Auditor changes with no clean explanation.
- Restatements in the last 3 years.
- CFO turnover ≥ 2 in 3 years.
- Operating cash flow persistently < 70% of net income without working-capital explanation.
- Material debt covenants breached or amended.
- Promotional CEO commentary that contradicts what the numbers say.

## Sources to prefer

- 10-K / 10-Q / 20-F / annual report (Chinese: 年报 / 中报).
- Proxy statements (DEF 14A) for comp + governance.
- Earnings-call transcripts — compare what management said 8 quarters ago vs today.
- SEC comment letters — often surface what's being asked about aggressively.
- **Avoid**: sell-side research summaries as primary source; they're useful for triangulation, not as ground truth.
