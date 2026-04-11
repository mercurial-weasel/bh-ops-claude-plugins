---
description: Finish and clean up a development branch
argument-hint: <branch description>
---

# Finish Branch

## Your Mission

Verify the current branch is ready to integrate and present options to the user.

## Verification

1. Run the full test suite — show actual output (do not summarize)
2. Run type-check if available — show actual output
3. Check for uncommitted changes
4. Show commit log since branching from `$BASE_BRANCH`

## Present Options

After verification, present exactly these 4 options:

1. **Merge to $BASE_BRANCH** — squash merge, delete branch
2. **Open Pull Request** — push branch, create PR with summary
3. **Keep branch** — leave as-is for later
4. **Discard branch** — delete branch and all changes (requires typing DISCARD to confirm)

Wait for the user to choose. Do not proceed without explicit selection.

## Output

Write a completion summary to `$ARTIFACTS_DIR/finish.md` with:
- Test results
- Option chosen
- Actions taken (merge commit, PR URL, etc.)
