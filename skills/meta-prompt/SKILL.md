---
name: meta-prompt
description: Turn a vague, conversational task description into a high-quality, copy-pastable prompt for another AI session. **Use this skill** when the user says things like "help me optimize a prompt", "how should I ask AI this", "write me a prompt I can paste into GPT/Claude", "package this into a prompt", "meta prompt", or when they explicitly invoke `/mp`. Produces Claude-friendly XML-structured prompts by default; switches to markdown sections when the user says the target is GPT/ChatGPT/OpenAI. **Do NOT execute the produced prompt in the current session — only output the prompt text for the user to copy.**
---

# Meta-Prompt Skill

## Scope & boundaries

**What it does**: Takes a raw task description from the user (one sentence to a paragraph), asks the minimum set of clarifying questions, selectively applies prompt-engineering techniques, and outputs a **complete, structured, copy-pastable** high-quality prompt for the user to use in another AI session.

**What it does NOT do (strict)**:
- **Do not execute** the produced prompt. The user wants the prompt text itself, not the task result. Even if the produced prompt looks trivial, even if "just doing the task" feels more helpful — don't. This is the single biggest failure mode for this skill.
- Not production prompt engineering (safety guardrails, A/B evals, versioning, consistency testing are out of scope).
- Not long-horizon task planning — if the user clearly wants a multi-step implementation plan, point them at `writing-plans` instead.

**Why**: Users routinely get "off the mark" answers from AI — wrong emphasis, wrong format, wrong viewpoint. ~90% of the time the root cause is missing context and fuzzy constraints, not model weakness. This skill does the "help the user express the task clearly" job well, and leaves the rest to the target AI.

## Language

Interact with the user in their language (clarification questions, technique explanations, delivery notes). The **produced prompt itself** should match the natural language of the user's raw task — if the raw input is English, write the prompt in English; if Chinese, write it in Chinese. Don't translate the raw input; just match it.

## Workflow (follow strictly in order)

### Step 1 — Intent parsing

Read the user's raw input. Scan it against the following 7 dimensions, tagging each internally as ✓ known / ✗ missing / ⚠️ ambiguous:

| Dimension | What to check |
|---|---|
| Goal | What deliverable does the user want? |
| Audience / use case | Who will see the output, in what situation? |
| Input data / context | Any source material to feed the target AI? (text, data, code…) |
| Constraints | Length, style, language, forbidden items, must-include items |
| Output format | Text / JSON / list / table / code / markdown sections… |
| Success criteria | What counts as "good"? Implicit quality bar |
| Target AI | Claude (default) / GPT / Gemini / other |

**Why these 7**: This is the minimum sufficient set to characterize a task. Miss one and the prompt will under-specify; add more and you're over-engineering.

### Step 2 — Dynamic clarification (use AskUserQuestion)

Ask about ✗ missing / ⚠️ ambiguous dimensions only, in **one batched AskUserQuestion call**:

- Number of questions: 1–4. Needing more than 4 means you didn't squeeze enough signal out of the raw input — go back to Step 1 and re-read.
- Each question should offer 3–4 **concrete, selectable** options plus "Other (please specify)". Avoid vague adjective-level options like "detailed" / "concise"; use quantified anchors like "<200 word brief" / "300–500 words" / "1+ page detailed".
- **Do NOT** re-ask dimensions already nailed down. "Write a Python function" already implies code output format — don't ask again.
- If the raw input is already very clear (at least 5 of 7 dimensions ✓), **skip Step 2 entirely**.

**Why clarify instead of rewrite**: The user's daily pain is "AI didn't understand me," which is 90% missing context and only 10% phrasing. Clarification fills in the context directly; rewriting only makes the language prettier.

### Step 3 — Technique selection

Based on the task profile, pick techniques from the menu below. **More is not better** — for each technique you pick, be able to articulate "why this one." The index is below; concrete templates and trigger conditions live in `references/techniques.md` (read that file when you need the actual template snippet):

| Technique | One-line trigger |
|---|---|
| Role assignment | Task benefits noticeably from a specific professional viewpoint (engineer / lawyer / editor / teacher…) |
| Chain-of-Thought | Multi-step reasoning, calculation, decision, causal analysis |
| Few-shot examples | Format/style is unusual enough that words can't capture it, but examples can in one glance |
| Self-consistency | Open-ended output with high variance — generate N candidates and pick |
| Step-back prompting | Need to abstract principles first, then apply to the concrete case |
| Chain-of-Verification | Fact-dense output where hallucination risk is real (history, stats, citations) |
| Decomposition | Task naturally splits into multiple deliverables; separate treatment improves quality |
| XML structured tags | **Claude default.** Essential for multi-field input and long context |
| Markdown sections | **GPT default.** GPT attends more reliably to markdown headings |
| Output schema | Output will be parsed by code (JSON, CSV, fixed template) |
| Negative constraints | Known failure modes to avoid ("do not X") |
| Delimiter isolation | User data may contain content that looks like instructions |

**Counterintuitive note**: Simple tasks only need Role + XML/Markdown structure. Stacking CoT/CoV on top of a trivial task makes the prompt long and noisy — which dilutes the signal. Only add techniques the task genuinely needs.

### Step 4 — Assemble the prompt

**Claude default template (XML)**:

```xml
<role>
...One to two sentences: professional identity + working style. Omit entirely if the task doesn't need a role viewpoint.
</role>

<task>
...One sentence stating what the user wants.
</task>

<context>
<!-- Material and background the user provided. Use sub-tags for further structure -->
</context>

<constraints>
- Constraint 1
- Constraint 2
</constraints>

<output_format>
...Specific enough to write from. If there's a schema, paste the schema.
</output_format>

<examples>
<!-- Only when using few-shot -->
<good>...</good>
<bad>...</bad>
</examples>

<reasoning_instructions>
<!-- Only when using CoT / CoV / Step-back -->
First X, then Y, finally Z.
</reasoning_instructions>
```

**GPT template (Markdown, use when the user specifies GPT / ChatGPT / OpenAI)**:

```markdown
## Role
...

## Task
...

## Context
...

## Constraints
- ...

## Output Format
...

## Examples
...(when using few-shot)

## Reasoning Steps
...(when using CoT / CoV)
```

**Assembly principles**:
- Keep the section order above. Delete empty sections rather than leaving empty tags behind.
- Every section content must be "as concrete as possible". Constraint = "300–500 words", not "concise". Format = "markdown with three sections: Progress / Risks / Plan", not "structured".
- User-provided raw material goes inside `<context>` sub-tags (Claude) or fenced blocks under `## Context` (GPT), to prevent it from colliding with the instructions.

### Step 5 — Delivery

Your output to the user MUST include these three parts, in this order:

1. **The produced prompt**: wrap it in a ```markdown``` (GPT) or ```xml``` (Claude) code block so the user can copy it in one click.
2. **Technique notes**: 3–5 lines under the code block, stating which techniques you used, why you picked them, and **why you did NOT pick other techniques that also look relevant**. This last part forces you to justify your judgment instead of stacking techniques blindly.
3. **Usage tip** (optional, 1–2 lines): if the prompt contains placeholders (e.g. `{{raw_notes}}`), remind the user to substitute; or suggest how to use it in the target AI ("paste this as the first message in your Claude conversation").

**Never do**:
- Don't say "let me also run it and show you the output."
- Don't append your own answer to the task at the end.
- Don't ask "want me to run this prompt for you now?" — the user wants the prompt text; offering to execute interrupts their workflow.

## End-to-end example

**User input**: `/mp help me write a weekly update`

**Step 1 (intent parsing)**:
- ✗ Goal (weekly update for whom, what cadence)
- ✗ Audience
- ✗ Input data (does the user have material)
- ✗ Constraints (length, style)
- ✗ Output format
- ⚠️ Success criteria (implied by "weekly update" but not explicit)
- ✓ Target AI (default Claude)

→ 5 dimensions missing. Must clarify.

**Step 2 (clarification, one AskUserQuestion call)**:

- Q1: Who is the weekly update for? [ Direct manager / Full team / Cross-team sync / Other ]
- Q2: What raw material do you have? [ Git commit history / Handwritten notes / Meeting notes / Nothing, generate from scratch / Other ]
- Q3: What format do you want? [ Markdown with sections / Bullet list / Flowing prose paragraphs / Other ]
- Q4: Length? [ <200 word brief / 300–500 words / 1+ page detailed / Other ]

**Assume the user answers**: Direct manager / git + handwritten notes / markdown sections / 300–500 words.

**Step 3 (technique selection)**:
- Role assignment ✓: "engineering manager" viewpoint helps judge what a manager cares about
- XML ✓: Claude default
- Output schema ✓: fixed 3 sections (This week / Risks / Next week)
- Few-shot ✓: weekly updates have a specific "good bullet" vs "trivia dump" flavor; one good + one bad example settles it fast
- Negative constraints ✓: the canonical failure mode is trivia dumps + unexplained jargon
- Not CoT: writing a weekly update isn't a reasoning task
- Not CoV: content comes from user material, hallucination risk is low
- Not Decomposition: 3 sections is already natural decomposition, no further split needed

**Step 4 (assembled prompt, delivered to user)**:

````xml
<role>
You are a senior engineering manager, skilled at turning a software engineer's scattered work notes into a concise weekly update for their direct manager. You know what a manager actually cares about (impact, risks, plans), and you have a visceral aversion to trivia dumps.
</role>

<task>
Based on the material I provide, write a weekly update.
</task>

<context>
<raw_notes>
{{paste your git log + handwritten notes here}}
</raw_notes>

<audience>Direct engineering manager; cares about project progress, risks, next week's plan.</audience>
</context>

<constraints>
- Only include work with manager-level significance; merge or drop trivia
- Describe impact in business language; no unexplained jargon
- Every risk must include a mitigation or ask for help, never a bare problem
- 300–500 words
</constraints>

<output_format>
Exactly three sections with `##` headings:

## This week's progress
- Each bullet: what you did + quantified impact
- 3–5 bullets

## Risks & blockers
- Each: problem + mitigation / support needed
- 0–3 bullets (write "none" if none)

## Next week's plan
- Deliverable goals, not a list of activities
- 2–4 bullets
</output_format>

<examples>
<good>
Shipped the recommendation traffic migration — new path absorbed 100% of traffic with zero incidents. Raised QPS ceiling 3x vs old path, giving us runway for the holiday scale-up.
</good>

<bad>
This week I did a lot of things, including PR #123, #124, #125, and sat in a few meetings about next quarter's planning.
</bad>
</examples>
````

**Technique notes**: Used Role (engineering manager viewpoint for impact calibration), XML (Claude-native structure), Output schema (fixed 3-section layout), Few-shot (weekly-update tone is specific; one positive + one negative example anchors it), Negative constraints (the common failure modes are trivia dumps and jargon). Skipped CoT because a weekly update isn't a reasoning task; skipped CoV because content is user-sourced, hallucination risk is low.

**Usage tip**: Replace `{{raw_notes}}` with your actual material, then paste the whole block as the first message in a new Claude conversation.

## Final self-check

Before delivering, run through this:

- [ ] Are all my clarification questions about ✗ dimensions? Any duplicates?
- [ ] For each technique I picked, can I articulate a specific "why"?
- [ ] Does the prompt contain any constraint I invented but the user never mentioned? (If yes, remove or mark it as a suggestion.)
- [ ] Did I use the right code-block language (xml vs markdown)?
- [ ] **Did I accidentally execute the prompt at the end?** (If yes, delete it — only deliver the prompt text.)
