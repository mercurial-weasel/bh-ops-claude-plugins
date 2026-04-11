---
name: before-you-build
description: >
  Viability gate that runs before brainstorming. Uses backwards decomposition
  against vault context to answer "should I build this at all?" in 20 minutes.
  Use when the user says "should I build", "is this worth it", "before I start",
  "validate this idea", "viability check", "what would need to be true for",
  "backwards from", or presents an idea that implies significant build/commercial
  commitment. Produces Go, Conditional Go, Park, or Task-only verdicts.
---

# Before You Build

Viability gate that prevents premature commitment. Uses backwards decomposition
to surface what must be true for an idea to work, then evaluates those conditions
against vault context.

**This skill gates brainstorming, not replaces it.** Ideas that pass go to
`/superpowers:brainstorming` with constraints pre-loaded. Ideas that don't pass
get parked with honest reasoning. Tasks that aren't ideas get routed to GitHub
issues directly.

---

## Pre-Filter

Run these two checks before the full assessment. Either can short-circuit the flow.

### Check 1: Is this just a task?

If the idea resolves to a single action with no build component, no commercial
complexity, and no unknowns — it's not an idea, it's a task.

**Examples:** "Introduce Mark Tovey to the Northwind Utilities team", "Send Brett that article",
"Book a follow-up with Jonathan"

**Action:** Skip the assessment. Offer to create a GitHub issue or vault action directly.

### Check 2: Is this already in flight?

Search for existing work on the same or adjacent topic:

```
docs/superpowers/specs/*.md     — existing specs
docs/superpowers/plans/*.md     — existing plans
companies/*/registry.md         — engagement context
research/assessments/*.md       — prior viability assessments
```

Also search GitHub issues on `bh-ops-vault` for matching titles.

**If found, offer three options:**

> "You already have [spec/plan/assessment] for X from [date]. Options:
> 1. **Revisit** — pick up where you left off
> 2. **Assess as new** — treat this as a fresh idea, ignore prior work
> 3. **Design review** — the existing spec is the problem, not the idea

Option 3 triggers a review of why prior work stalled. Same principle as the
two-plan rule in code-quality-remediate: if the approach was wrong, don't
re-run it — review it.

---

## Core Flow

### Step 1 — Parse the Idea

Extract from the user's input:

- **Who:** Person, company, archetype, or unknown
- **What:** Build, offer, relationship, process, or financial target
- **Implied outcome:** What "working" would look like

If the input is a financial target ("$25k/month") or a state of readiness
("hire a dev"), note that the decomposition will work backwards from a
measurable target rather than a product concept.

### Step 2 — Load Vault Context

Pull relevant context and classify the density:

| Source | Where to look | What to extract |
|--------|--------------|-----------------|
| Contact profiles | `contacts/<name>.md` | Role, company, archetype, last contact, attitude |
| Engagement registries | `companies/<company>/registry.md` | Stage, history, commercial relationship |
| Offerings | `offerings/*.md` | Existing offerings that might already cover this |
| Mission filters | `my-companies/mission.md` | David Bacchus test, 90-day extraction rule |
| Prior specs/plans | `docs/superpowers/specs/*.md`, `docs/superpowers/plans/*.md` | Adjacent or overlapping work |

**Classify density:**

- **Vault-rich:** Contact exists, engagement history present, archetype matched.
  Assessment will be specific and high-confidence.
- **Vault-sparse:** Missing contact, no engagement, no archetype. Assessment will
  surface assumptions rather than evaluate evidence.

Both modes are useful. Vault-sparse output is arguably more valuable for genuinely
new ideas — it makes implicit assumptions explicit before momentum takes over.

### Step 3 — Run Dimensions (Adaptive)

**Always run:**

**Value Fit**
> Does the target actually have this problem? Is it a real pain or an assumed one?

- Vault-rich: check contact notes, meeting debriefs, engagement registry for evidence
  of the pain. Quote specific mentions if found.
- Vault-sparse: state the assumption explicitly. "We're assuming X has problem Y
  based on [archetype/sector/analogy]. No direct evidence."

**90-Day Test**
> What does "working" look like concretely in 90 days? Describe it.

If you can't describe a specific, observable state ("Sharon uses the dashboard
weekly to prep her Monday programme reviews"), the idea isn't clear enough to
assess. This is a finding, not a blocker — note it as a knowledge gap.

**Knowledge Gaps**
> What don't we know? Classify each gap.

- **Resolvable:** Can be answered through a specific action with a known timeline.
  Output: task with deadline. "Find out X at April 25 meeting."
- **Structural:** Cannot be resolved without the target's input or real-world testing.
  Output: risk statement. "We can't know if Sharon would adopt this without asking her."

---

**Run if commercial context exists** (engagement registry found, offering match, or
financial target in the input):

**Commercial Anchor**
> Does this connect to revenue, an offering, a pipeline opportunity? Or is it a
> solution looking for a business case?

Check: does an offering definition exist that covers this? Is there an active
engagement with the target company? What stage is it at?

**Adoption Path**
> How does this get in front of users? Who puts it there? What replaces it if they stop?

Check: is there an internal champion? Is there a deployment model? Is this a one-off
demo or a recurring tool?

---

**Run if build is implied** (the idea involves making something — code, a tool,
a platform, a product):

**Build Cost vs Alternatives**
> Could a spreadsheet, a conversation, or an existing tool solve this? Is building
> the right response?

Check: does a simpler solution exist? Is the complexity in the problem or in the
solution? Would a 2-hour conversation achieve 80% of the outcome?

### Step 4 — Mission-Specific Filters

These surface by name when vault context triggers them. They are calibrated to
Dave's specific situation and carry more weight than the generic dimensions.

**David Bacchus Test**
- **Triggers when:** Target is in Frequency context, or target is a senior practitioner
- **Question:** "Would David understand what this does in 30 seconds?"
- **If no:** The idea is too abstract for the relationship. This doesn't mean the idea
  is bad — it means the relationship isn't ready for it, or the framing needs work.

**90-Day Extraction Rule**
- **Triggers when:** Commercial anchor is weak, or significant build investment required
- **Question:** "If this doesn't work in 90 days, can you walk away clean?"
- **If no:** The commitment/reward ratio is wrong. Either reduce the commitment (build
  less, use existing components) or increase the reward certainty (get commitment
  before building).

### Step 5 — Classify All Knowledge Gaps

Consolidate gaps from all dimensions. For each gap:

| Type | Definition | What it becomes |
|------|-----------|-----------------|
| **Resolvable** | Answerable through a specific action with known timeline | Task with concrete deadline/trigger |
| **Structural** | Requires target's input or real-world testing to resolve | Risk in the assessment |

**Resolvable tasks must be specific and falsifiable:**
- "Sharon confirms she spends 3+ hours/week on this" (April 25 catch-up)
- "AB Smith intro produces at least one warm response" (by May 10)

NOT: "learn more about needs" or "validate the market"

**Load-bearing test for resolvable gaps:** Would the brainstorm produce a meaningfully
different design depending on this gap's answer? If yes, it's load-bearing and the
verdict is Conditional Go, not Go.

### Step 6 — Render Verdict

#### Go

All core dimensions pass. No load-bearing gaps. Proceed to brainstorm.

**Output:** One paragraph of reasoning, then hand off to `/superpowers:brainstorming`
with this constraint block injected as a named section:

```markdown
## Viability Constraints (from /before-you-build assessment)

### Conditions That Must Hold
- <condition 1 — specific, from the assessment>
- <condition 2>

### Structural Risks (design around these)
- <risk 1 — cannot be resolved, must be accommodated>

### Resolvable Tasks (address during or after brainstorm)
- <task 1 — concrete, with deadline/trigger>
```

The brainstorm skill treats Conditions as requirements, Risks as design constraints,
Tasks as a checklist. It does not re-derive or reinterpret them.

**Vault-sparse Go caveat:** When issuing Go from a vault-sparse assessment, add:

```markdown
### Confidence: Low — vault-sparse assessment
This Go is based on assumptions, not evidence. The brainstorm should treat
the Conditions section as hypotheses to validate, not confirmed requirements.
Consider running /research-person or /company-ingest before committing to
implementation.
```

#### Conditional Go

Assessment passes, but resolvable gaps are **load-bearing**. Brainstorming before
they're resolved would build on unconfirmed assumptions.

**Output:**
1. Vault note at `research/assessments/YYYY-MM-DD-<idea-slug>.md` with full assessment
2. GitHub issue for each load-bearing task (so they're trackable)
3. Explicit gate: "Proceed to brainstorm only after these tasks complete:"
   - Task 1 (deadline/trigger)
   - Task 2 (deadline/trigger)

#### Park

Core dimensions don't pass, or confidence is too low to commit.

**Output:** Vault note at `research/assessments/YYYY-MM-DD-<idea-slug>.md`

The `what-would-change-verdict` frontmatter field is the most important part.
It must be:
- **Specific:** Not "more information" but "Sharon confirms 3+ hours/week on this"
- **Falsifiable:** There's a way to know if the condition was met or not
- **Has a natural trigger:** A meeting, a trip, a deliverable — not open-ended
- **Singular or very few:** If 5 things need to change, the idea is further from
  viable than "park" suggests

#### Task-Only

Pre-filter determined this isn't an assessable idea. Just a thing to do.

**Output:** Offer to create GitHub issue or vault action. No assessment artifact.

---

## Vault Note Format

Used for Park and Conditional Go verdicts.

```markdown
---
type: idea-assessment
date: YYYY-MM-DD
idea: "<one-line description>"
verdict: park | conditional-go
confidence: high | medium | low
linked-contacts:
  - "[[contact-name]]"
linked-companies:
  - "[[company-name]]"
what-would-change-verdict: "<specific, falsifiable condition>"
tags:
  - idea-assessment
  - <domain-tag>
---

# Idea Assessment: <idea name>

## The Idea
<One paragraph: what was proposed and why>

## Verdict: <Park | Conditional Go>
<One paragraph: the reasoning>

## Dimensions

### Value Fit
<Finding — with vault evidence if available>

### 90-Day Test
<What "working" looks like, or why it couldn't be described>

### Knowledge Gaps
- **Resolvable:** <gap> → <task with deadline>
- **Structural:** <gap> → <risk statement>

### Commercial Anchor (if assessed)
<Finding>

### Adoption Path (if assessed)
<Finding>

### Build Cost vs Alternatives (if assessed)
<Finding>

## Mission Filters (if triggered)
- **David Bacchus test:** <pass/fail and why>
- **90-day extraction rule:** <pass/fail and why>

## Conditions for Revisiting
<Specific, falsifiable conditions — not "more information">
```

**Target: under 100 lines.** This is a decision record, not an analysis document.

---

## Confidence Criteria

| Level | Definition |
|-------|-----------|
| **High** | Vault-rich, all run dimensions answered, structural unknowns exist but none are load-bearing |
| **Medium** | Vault-sparse OR 1+ load-bearing structural unknowns OR one adaptive dimension couldn't be assessed |
| **Low** | Mostly assumptions, would need significant research before acting |

---

## Backwards Decomposition — Stopping Condition

Decomposition stops when it hits:

1. **Something that already exists** — "we have this" (no further decomposition)
2. **A pure decision** — "someone needs to choose this" (becomes a decide task or risk)
3. **An atomic handoff** — "this becomes a spec" or "this becomes an issue"

### Two-Level Horizon

Decompose two levels deep maximum:

- **Level 1 — Immediate preconditions:** What must be true 30-60 days before the target?
- **Level 2 — Current gaps:** What's missing right now against those preconditions?

Anything deeper is either already handled or premature.

### Leaf Node Routing

Each leaf in the decomposition tree gets tagged:

- **Build** → becomes a spec via brainstorm pipeline
- **Decide** → vault document, architecture review, or design session
- **Do** → GitHub issue, calendar action, vault task

### Worked Example — "Hire a dev by Q3"

**Level 1** (immediate preconditions — what must be true 30-60 days before):
- Revenue consistently above $X/month (threshold from BH financial model)
- At least one product stable enough to hand off work on
- Defined scope of what the dev would own (not "help with everything")
- Pipeline visibility showing the revenue is sustainable, not a spike

**Level 2** (current gaps against those preconditions):
- Revenue is at $Y/month → **resolvable gap**, depends on Q2 pipeline closing
- No product has documented handoff scope → **resolvable task**, write it
- Pipeline visibility requires forecast model update → **resolvable task**
- "Is the revenue sustainable" is unknowable today → **structural unknown**

Decomposition stops here. "How to close Q2 pipeline" is a level 3 question
that has its own pipeline/nurture workflow — don't decompose into it.

### Worked Example — "$25k USD profit/month by Q4"

**Level 1** (immediate preconditions — what must be true by September):
- Revenue mix: which offerings at what price points sum to $25k profit?
- Client count: how many clients at what tier? (1x$25k or 5x$5k are different paths)
- Pipeline: enough pipeline in July-August to close by September
- Delivery capacity: can Dave deliver that volume alone, or does hiring come first?

**Level 2** (current gaps against those preconditions):
- Revenue mix unknown → **resolvable task**, model the 3-4 most likely combinations
- Current pipeline is N clients at stage X → **resolvable**, check via /nurture
- Delivery capacity depends on product vs consulting mix → **structural unknown**
- No Melbourne clients yet → **resolvable gap**, depends on April/May trip outcomes

Each leaf routes differently:
- "Model revenue combinations" → **build** (spreadsheet or vault calculation)
- "Check pipeline via /nurture" → **do** (run the skill)
- "Consulting vs product mix" → **decide** (design session / architecture review)
- "Melbourne pipeline" → **conditional** (depends on trip, not buildable now)

---

## Scope Boundaries

- Single idea per invocation. Multiple ideas → assess sequentially.
- Does not do deep research. Notes gaps, doesn't launch `/research-person`.
- Does not write specs, plans, or code. Terminal state is a verdict.
- Surfaces existing work before assessing — user chooses revisit, fresh, or review.
- Does not assess pure tasks (pre-filter catches these).
