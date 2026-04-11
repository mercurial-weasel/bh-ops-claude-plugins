---
description: Implement tasks from a plan using TDD
argument-hint: <plan reference>
---

# Implement Tasks

## Your Mission

Read the implementation plan from `$ARTIFACTS_DIR/plan.md` and execute each task using strict TDD.

## Iron Law

No production code without a failing test first. Every change follows RED-GREEN-REFACTOR:

1. **RED:** Write a failing test that defines the expected behavior
2. **GREEN:** Write the minimum code to make the test pass
3. **REFACTOR:** Clean up while keeping tests green

## Process

For each task in the plan:
1. Read the task requirements
2. Write the failing test (run it, confirm it fails)
3. Write the implementation (run test, confirm it passes)
4. Run the full test suite (confirm no regressions)
5. Type-check: `bun run tsc --noEmit` (if tsconfig exists)
6. Commit with the exact message from the plan

## Verification Before Completion

After all tasks:
1. Run the full test suite — show the output
2. Run type-check — show the output
3. Do NOT claim tests pass without running them

## Output

Write a summary of what was implemented to `$ARTIFACTS_DIR/implementation.md` including:
- Tasks completed
- Test results (paste actual output)
- Any deviations from the plan and why
