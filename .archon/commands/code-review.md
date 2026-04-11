---
description: Review code for spec compliance and quality
argument-hint: <branch or description>
---

# Code Review

## Your Mission

Review the current branch against the spec at `$ARTIFACTS_DIR/spec.md` and the plan at `$ARTIFACTS_DIR/plan.md`.

## Two-Pass Review

### Pass 1: Spec Compliance

Compare implementation to spec requirements:
- Is everything that was specified actually built?
- Is anything built that was NOT specified?
- Are there misinterpretations of requirements?

For each finding, cite file:line and the specific spec requirement.

### Pass 2: Code Quality

Review for:
- Test coverage — are all behaviors tested?
- Error handling — are failure modes covered?
- Naming — do names match what things do?
- Complexity — is anything unnecessarily complex?
- Security — any injection, XSS, or data exposure risks?

### Severity Levels

- **Critical:** Blocks release. Must fix. (Security, data loss, spec violation)
- **Important:** Should fix. (Missing tests, poor error handling, unclear names)
- **Minor:** Nice to fix. (Style, minor refactors)

## Output

Write the review to `$ARTIFACTS_DIR/review.md` with:
- Summary (overall assessment)
- Spec compliance findings (with file:line references)
- Code quality findings (with file:line references)
- Each finding tagged with severity
