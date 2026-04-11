---
description: Fix issues found in code review
argument-hint: <review reference>
---

# Fix Review Issues

## Your Mission

Read the code review from `$ARTIFACTS_DIR/review.md` and fix all critical and important issues.

## Process

For each critical/important issue:
1. Read the finding and understand the problem
2. If you disagree, explain why with evidence (code references, test output) — do not silently ignore
3. If you agree, fix it
4. Verify the fix (run tests, check the specific scenario)

## Rules

- Fix all critical issues — no exceptions
- Fix all important issues unless you can justify why the reviewer is wrong
- Minor issues: fix if trivial, skip if not
- Run the full test suite after all fixes
- Do not introduce new issues while fixing old ones

## Output

Write a summary of fixes to `$ARTIFACTS_DIR/review-fixes.md` including:
- Each issue addressed (fixed or pushed back with reasoning)
- Test results after fixes
- Any remaining items and why they were deferred
