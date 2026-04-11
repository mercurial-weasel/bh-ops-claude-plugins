---
name: code-quality-remediate
description: >
  Generate and execute a phased remediation plan from a code quality audit.
  Use when the user says "remediate", "fix the audit findings", "code quality fix",
  "improve the score", "address the audit", or after running a /code-quality audit.
  Reads the most recent audit file, generates a phased plan with a fixed exit score,
  and optionally executes via subagent-driven development.
---

# Code Quality Remediation

Takes a code quality audit report and produces a bounded, phased remediation plan.
Optionally executes the plan via subagent-driven development.

**This skill exists because remediation without structure causes cascade failure.**
Evidence: 10 plans in one day on a single repo, target moving from 5.0 to 8.5 with
no stop condition. The rules below prevent that.

---

## Hard Rules (Non-Negotiable)

1. **One plan per audit.** Never spawn a follow-up remediation plan from this skill.
   If the plan can't reach the target, revise the target, don't create another plan.

2. **Fixed exit score.** The plan declares a target score upfront (typically +1.5 to +2.0
   from current). Execution stops when the target is reached OR when all phases complete,
   whichever comes first. No moving goalposts.

3. **Plan cap: 1,500 lines.** If the plan exceeds this, the audit findings are too broad.
   Go back and triage the audit — pick the top 3-5 findings by impact, not all of them.

4. **Max 4 phases.** Each phase must be independently shippable. If you need more than 4,
   the scope is wrong.

5. **Two-plan rule.** If a domain already has 2 remediation plans within 14 days, the next
   action is a design review, not a third plan. The architecture is wrong, not the code.

---

## How to Run

```
/dev:code-quality-remediate                    # auto-detect latest audit
/dev:code-quality-remediate --target 7.5       # set explicit exit score
/dev:code-quality-remediate --plan-only        # generate plan, don't execute
/dev:code-quality-remediate --audit path.md    # use specific audit file
```

---

## Step 1 — Load the Audit

1. Find the most recent audit file in `docs/code-quality/` (or use `--audit` path)
2. Extract:
   - **Current score** (overall and per-dimension)
   - **All findings** with severity (Critical, Important, Minor)
   - **Previously resolved** items (if this isn't the first audit)
   - **Persistent issues** that were flagged in prior audits but never fixed

If no audit file exists, stop and tell the user to run `/code-quality` first.

---

## Step 2 — Triage Findings

Not all findings are worth fixing. Triage by **impact × effort**:

| Priority | Criteria | Action |
|----------|----------|--------|
| **P1 — Fix now** | Critical severity, low effort, blocks other work | Include in Phase 1 |
| **P2 — Fix this plan** | Important severity, or Critical + high effort | Distribute across phases |
| **P3 — Defer** | Minor severity, or cosmetic, or requires design decision | Document in plan as explicitly deferred |
| **P4 — Won't fix** | Accepted tech debt, library limitations, not worth the churn | Document with rationale |

**Persistent issues** (flagged in 2+ prior audits) get auto-promoted one priority level.
If something has been flagged 3 times and never fixed, it's P1 regardless of severity.

**P4 re-confirmation:** If a "won't fix" item from a prior plan reappears in the current
audit, it must be explicitly re-confirmed as P4 with updated rationale — not silently
inherited. Agents will otherwise just carry forward the deferral without re-evaluating
whether the original reason still holds.

---

## Step 3 — Set the Target

Calculate a realistic exit score:

- **Current score < 5.0**: Target +2.0 (infrastructure is missing)
- **Current score 5.0-6.5**: Target +1.5 (patterns need establishing)
- **Current score 6.5-7.5**: Target +1.0 (refinement phase)
- **Current score > 7.5**: Target +0.5 (diminishing returns)

User can override with `--target`. Never set a target above 9.0 — that's maintenance, not remediation.

---

## Step 4 — Generate the Plan

Write the plan to `docs/superpowers/plans/YYYY-MM-DD-code-quality-remediation.md`.

### Plan Structure

```markdown
# Code Quality Remediation Plan

**Audit source:** docs/code-quality/YYYY-MM-DD-audit.md
**Current score:** X.X/10
**Target score:** Y.Y/10
**Exit condition:** Target reached OR all phases complete

## Triage Summary

| Finding | Severity | Priority | Phase |
|---------|----------|----------|-------|
| ... | Critical | P1 | 1 |

## Deferred (P3/P4)
- [finding] — reason for deferral

## Phase 1: [Name] (estimated: N tasks)
**Goal:** [What this phase achieves, measurable]
**Dimension targets:** [Which scores should improve]

### Tasks
1. [Specific, atomic task with file references]
2. ...

## Phase 2: [Name]
...

## Verification
After each phase, re-run the relevant audit checks (not the full audit)
to confirm the dimension scores improved as expected.
```

### What makes a good phase:

- **Phase 1** should always be infrastructure: error taxonomy, env centralisation,
  Zod schemas at boundaries. **Why first:** every subsequent phase produces code that
  needs error handling and validated inputs. Without infra, Phases 2-4 introduce
  the same gaps you're trying to fix.
- **Phase 2** should be type safety: eliminating `as any`, `v.any()`, adding
  validators. **Why second:** this is mechanical, high-impact, and gives the compiler
  the information it needs to catch regressions from Phase 3 restructuring.
- **Phase 3** should be structural: dependency direction fixes, module decomposition,
  interface segregation. **Why third:** restructuring is safer when types are tight —
  the compiler catches broken imports and shape mismatches immediately.
- **Phase 4** (if needed) should be coverage: tests for the code changed in Phases 1-3,
  not aspirational coverage goals. **Why last:** testing restructured code, not code
  that's about to be moved.

---

## Step 5 — Execute (unless --plan-only)

Present the plan to the user for approval. On approval:

1. Read the project's CLAUDE.md for non-negotiable rules
2. Execute via subagent-driven development (one task per subagent)
3. After each phase completes, run the phase verification checks below
4. If the target score is reached mid-plan, **stop**. Report remaining phases as
   "deferred — target reached" and move on.

### Phase Verification (lightweight, not a full audit)

Run only the checks relevant to what the phase changed:

| Phase | What to verify | Commands |
|-------|---------------|----------|
| **1 — Infrastructure** | env centralised, AppError adopted, Zod at boundaries | `grep -rn "process\.env\." src/ convex/ \| grep -v "lib/env"` (should be 0), `grep -rn "catch.*: any" src/` (should be 0), `tsc --noEmit` |
| **2 — Type safety** | as any eliminated, v.any() resolved, validators in place | `grep -rn "as any" src/ \| grep -v node_modules \| wc -l`, `grep -rn "v\.any()" convex/ \| wc -l`, `tsc --noEmit` |
| **3 — Structure** | no reverse deps, files under 500 lines, clean imports | `grep -rn "from.*stores/" src/utils/`, `find src/ -name "*.ts" -o -name "*.tsx" \| xargs wc -l \| sort -rn \| head -5`, `tsc --noEmit` |
| **4 — Coverage** | tests pass, new tests cover changed code | `npm test` or equivalent, check test file count vs previous |

`tsc --noEmit` runs after every phase — it's the cheapest regression detector.
If any verification fails, fix before proceeding to the next phase.

---

## Step 6 — Update the Audit Trail

After execution (or after plan-only generation):

1. If code was changed, run a fresh `/code-quality` audit
2. Update the project's README.md Code Quality field with the new score
3. Commit the plan and any new audit files

---

## Anti-Patterns to Avoid

- **Scope creep into features.** Remediation fixes structure, not functionality.
  If a finding requires new features (e.g., "add a design token system"), that's
  a separate spec/plan, not a remediation task.
- **Chasing 10/10.** Diminishing returns hit hard above 8.0. Stop at the target.
- **Remediation cascades.** One plan. Fixed target. No follow-ups from this skill.
  If more work is needed, it's a new audit → new triage → new plan cycle.
- **Fixing P3/P4 items.** If you deferred them for a reason, don't sneak them in.
