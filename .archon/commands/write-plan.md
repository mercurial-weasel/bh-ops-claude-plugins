---
description: Write an implementation plan with TDD steps from a spec
argument-hint: <feature name>
---

# Write Plan

## Your Mission

Read the spec from `$ARTIFACTS_DIR/spec.md` and produce an implementation plan with bite-sized tasks that follow TDD.

## Plan Structure

Each task must:
- Produce one passing test and one implementation file/function — that's the unit of work
- Have a clear deliverable (specific files created/modified)
- Include TDD steps: write failing test (RED), implement (GREEN), refactor (REFACTOR)
- Include the actual code for tests and implementation — no placeholders
- Specify the exact commit message using conventional commits format (e.g. `feat(scope): description`)

## Task Format

```
## Task N: [Name]

**Files:**
- Create/Modify: `path/to/file.ts`

- [ ] **Step 1: Write failing test**
[actual test code]

- [ ] **Step 2: Run test to verify it fails**
[exact command]

- [ ] **Step 3: Write implementation**
[actual implementation code]

- [ ] **Step 4: Run test to verify it passes**
[exact command]

- [ ] **Step 5: Commit**
[exact git command with message]
```

## Task Sequencing

Order tasks so the test suite passes after every commit. No task should introduce a failing test it doesn't also fix. If the spec has a dependency graph (A depends on B), implement B first. The plan should be buildable by executing tasks in order from top to bottom.

## Test Discipline

- Tests must not depend on counts or values from current data — assert structure and parse correctness, not specific record counts that will drift
- Every public function or CLI command in the spec needs a test in the plan — if the spec says "CLI subcommand with flags X, Y, Z" then a task must test that subcommand, not just the functions it calls
- Integration tests should verify the wiring (argument parsing, output format, exit codes), not just re-test the units

## Quality Checks

Before writing output:
- Every task has complete code (no "implement similar to above" or "add tests")
- No placeholder text
- Dependencies between tasks are explicit and ordering respects them
- File structure matches the spec
- Commit messages use conventional commits: `feat(scope): ...`, `test(scope): ...`, `fix(scope): ...`

## Self-Review

After writing the plan, re-read the spec's **Testing Strategy** and **Acceptance Criteria** sections. For each criterion, confirm a specific test in the plan covers it. If a criterion has no corresponding test, add a task. List the mapping at the bottom of the plan.

## Output

Write the implementation plan to `$ARTIFACTS_DIR/plan.md`.
