---
description: Independent audit of an implementation plan against its spec
argument-hint: <plan reference>
---

# Audit Plan

## Your Mission

You are an independent reviewer. You did NOT write this plan. Read the spec and the plan with fresh eyes and produce a structured critique.

Read:
- Spec: `$ARTIFACTS_DIR/spec.md`
- Plan: `$ARTIFACTS_DIR/plan.md`

## Audit Checklist

### 1. Acceptance Criteria Coverage

For each acceptance criterion in the spec's Testing Strategy section, check whether a specific test in the plan covers it. Report:
- Criterion → which task/test covers it
- Any criteria with NO corresponding test (these are gaps)

### 2. Dependency Ordering

Walk the task list top to bottom. After each task's commit, would the test suite pass? Flag any task that:
- Imports a module not yet created
- References a type not yet defined
- Introduces a test that depends on a later task's implementation

### 3. Test Quality

For each test in the plan:
- Does it test behavior or just call a function?
- Does it use hardcoded values from current data that will drift?
- Is CLI wiring tested (argument parsing, exit codes, output format) or only the underlying functions?

### 4. Implementation Completeness

For each function/module in the spec's Detailed Design:
- Is there a task that implements it?
- Does the implementation match the spec's interface (inputs, outputs, error handling)?
- Any spec requirements silently dropped?

### 5. Risk Flags

- Tasks that are too large (multiple files + complex logic in one task)
- Missing error handling paths that the spec calls for
- Assumptions about external state (file paths, data counts, environment)

## Output Format

Write the audit to `$ARTIFACTS_DIR/plan-audit.md` with this structure:

```
# Plan Audit

## Coverage Matrix
| Spec Criterion | Plan Task/Test | Status |
|---|---|---|
| criterion | Task N, test name | COVERED / GAP / PARTIAL |

## Dependency Issues
[list or "None found"]

## Test Quality Issues
[list or "None found"]

## Implementation Gaps
[list or "None found"]

## Risk Flags
[list or "None found"]

## Verdict
[APPROVE / REVISE — with summary of what needs fixing]
```
