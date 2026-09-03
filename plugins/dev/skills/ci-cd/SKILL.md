---
name: ci-cd
description: >
  Set up and maintain CI/CD pipelines for TypeScript/React projects.
  Use when the user says "set up CI", "add GitHub Actions", "pre-commit hooks",
  "add linting to CI", "automate quality checks", "set up husky", "configure CI/CD",
  "add a pipeline", "wire up GitHub Actions", or any variation of automating
  code quality, testing, or deployment checks.
  Produces a concrete implementation plan with all config files ready to commit.
---

# CI/CD Setup

Sets up pre-commit hooks (Husky + lint-staged) and GitHub Actions workflows for
TypeScript/React projects. Produces working config files tailored to the actual
stack and quality baseline of the repo.

**This skill produces files to commit, not just advice.**
Every output is a concrete file path and content ready for the agent to create.

---

## How to Run

1. Read the project's `package.json` to understand the stack (framework, test runner, linter)
2. Check for existing CI config: `.github/workflows/`, `.husky/`, `lint-staged.config.*`
3. Check the current quality baseline — don't add checks that will immediately fail
4. Read `CLAUDE.md` if present for project conventions
5. Produce the implementation plan below, tailored to what's found

**Do not add a check that the codebase currently fails.**
Every check added to CI must pass on the current codebase before it's wired in.
If a check would currently fail (e.g. `as any` violations still present), note it
as a "deferred check" with the condition that unblocks it.

---

## Opening Discovery Commands

```bash
# Understand the project shape
cat package.json | grep -A 30 '"scripts"'
cat package.json | grep -A 10 '"devDependencies"'

# Check for existing CI/CD
ls .github/workflows/ 2>/dev/null && cat .github/workflows/*.yml 2>/dev/null || echo "No workflows yet"
ls .husky/ 2>/dev/null || echo "No husky yet"
cat lint-staged.config.* 2>/dev/null || grep -A 10 '"lint-staged"' package.json 2>/dev/null || echo "No lint-staged yet"

# Check test runner and coverage
grep -n "vitest\|jest\|playwright\|cypress" package.json

# Check for ESLint config
ls .eslintrc* eslint.config.* 2>/dev/null

# Check for Prettier config
ls .prettierrc* prettier.config.* 2>/dev/null

# Check TypeScript config
cat tsconfig.json | grep -E '"strict"|"noEmit"|"skipLibCheck"'

# Current quality baseline — know what would fail before wiring checks
grep -rn "catch.*: any\|as any" src/ --include="*.ts" --include="*.tsx" 2>/dev/null | wc -l
grep -rn "import\.meta\.env\." src/ --include="*.ts" --include="*.tsx" 2>/dev/null | grep -v "lib/env" | wc -l
npx tsc --noEmit 2>&1 | wc -l

# Check for monorepo structure
ls packages/ 2>/dev/null && echo "Monorepo detected" || echo "Single package"
cat pnpm-workspace.yaml 2>/dev/null || echo "No pnpm workspace"
```

---

## Two Layers

CI/CD for a TypeScript project has two distinct layers with different purposes.
Understand both before implementing either.

### Layer 1 — Pre-commit (local, developer machine)

**Tool:** Husky + lint-staged
**When it runs:** Before every `git commit`, on staged files only
**Purpose:** Fast feedback on the files you're about to commit
**Speed requirement:** Must complete in under 10 seconds or developers bypass it with `--no-verify`

**What belongs here:**
- Code formatting (Prettier) — auto-fix, never blocks
- Linting (ESLint) — auto-fix where possible, block on errors
- Type check on changed files only (optional — can be slow)

**What does NOT belong here:**
- Full test suite (too slow)
- Circular dependency checks (whole-codebase scan)
- Build verification
- Custom architectural checks

### Layer 2 — GitHub Actions (remote, every push/PR)

**Tool:** GitHub Actions
**When it runs:** On every push and pull request
**Purpose:** Full quality gate — catches what pre-commit misses
**Speed requirement:** Under 5 minutes for the full suite

**What belongs here:**
- Full TypeScript check (`tsc --noEmit`)
- Full test suite
- Build verification
- Custom architectural checks (grep-based enforcement)
- Circular dependency check (madge)
- Storybook build (if packages/ui exists)
- Convex type check (if Convex backend)
- Package boundary checks (if monorepo)
- Security checks (no committed secrets)

---

## The Checks

Each check below has a **prerequisite** — the condition the codebase must meet before
this check can be added without immediately failing CI.

### Standard Checks (add immediately for any TypeScript project)

#### S1. TypeScript Compilation
```yaml
- name: Type check
  run: npx tsc --noEmit
```
**Prerequisite:** `npx tsc --noEmit` exits 0 on current codebase.
**What it catches:** Type errors, missing imports, schema drift between layers.

#### S2. Tests
```yaml
- name: Tests
  run: pnpm vitest run   # or: pnpm test
```
**Prerequisite:** Test suite passes locally.
**What it catches:** Regressions in business logic and utility functions.

#### S3. No Committed Secrets
```yaml
- name: No committed .env
  run: |
    if git ls-files | grep -q "^\.env$"; then
      echo "ERROR: .env is tracked by git"
      exit 1
    fi
```
**Prerequisite:** None — always safe to add.
**What it catches:** API keys, credentials accidentally committed.

#### S4. Lint
```yaml
- name: Lint
  run: npx eslint src/ --ext .ts,.tsx --max-warnings 0
```
**Prerequisite:** `eslint` exits 0 on current codebase (run with `--fix` first if needed).
**What it catches:** Code style violations, unused imports, accessibility issues.

---

### Architectural Checks (add after baseline is clean)

These checks encode hard-won architectural decisions so they can't quietly regress.
Each one corresponds to a specific pattern in the codebase.

#### A1. No catch-any blocks
```bash
count=$(grep -rn "catch.*: any" src/ convex/ \
  --include="*.ts" --include="*.tsx" \
  | grep -v "_generated\|node_modules" | wc -l)
if [ "$count" -gt "0" ]; then
  echo "ERROR: Found $count catch(err: any) blocks. Use catch(err: unknown) with toAppError()."
  grep -rn "catch.*: any" src/ convex/ --include="*.ts" --include="*.tsx" | grep -v "_generated"
  exit 1
fi
```
**Prerequisite:** Zero `catch(err: any)` in codebase.
**What it catches:** Type-unsafe error handling that masks runtime bugs.

#### A2. Env vars read only in central config
```bash
count=$(grep -rn "import\.meta\.env\.\|process\.env\." src/ \
  --include="*.ts" --include="*.tsx" \
  | grep -v "src/lib/env\|src/config/env\|node_modules" | wc -l)
if [ "$count" -gt "0" ]; then
  echo "ERROR: Env vars read outside central config file."
  grep -rn "import\.meta\.env\.\|process\.env\." src/ --include="*.ts" --include="*.tsx" \
    | grep -v "src/lib/env\|src/config/env\|node_modules"
  exit 1
fi
```
**Prerequisite:** All env reads centralised in `src/lib/env.ts` or equivalent.
**What it catches:** Env vars read deep in business logic — causes confusing runtime crashes.

#### A3. No utils importing from pages
```bash
count=$(grep -rn "from.*['\"].*pages/" src/utils/ src/lib/ src/stores/ \
  --include="*.ts" --include="*.tsx" 2>/dev/null | wc -l)
if [ "$count" -gt "0" ]; then
  echo "ERROR: Reverse dependency — utils/lib/stores importing from pages/."
  grep -rn "from.*['\"].*pages/" src/utils/ src/lib/ src/stores/ --include="*.ts" --include="*.tsx"
  exit 1
fi
```
**Prerequisite:** No reverse dependencies in current codebase.
**What it catches:** Dependency direction violations that cause circular import chains.

#### A4. No stores importing from hooks or components
```bash
count=$(grep -rn "from.*['\"].*hooks/\|from.*['\"].*components/" src/stores/ \
  --include="*.ts" 2>/dev/null | wc -l)
if [ "$count" -gt "0" ]; then
  echo "ERROR: Store importing from hooks/ or components/."
  grep -rn "from.*hooks/\|from.*components/" src/stores/ --include="*.ts"
  exit 1
fi
```
**Prerequisite:** Stores/ directory only contains actual Zustand stores.
**What it catches:** Inverted dependency direction that makes stores untestable.

#### A5. Circular dependency check (requires madge)
```bash
npx madge src/ --circular --extensions ts,tsx
if [ $? -ne 0 ]; then
  echo "ERROR: Circular imports detected."
  exit 1
fi
```
**Prerequisite:** `npx madge src/ --circular` returns nothing on current codebase.
**What it catches:** Circular import chains that cause undefined values at runtime.
**Note:** Add `madge` to devDependencies first: `pnpm add -D madge`

#### A6. packages/ui has no app imports (monorepo only)
```bash
count=$(grep -rn "from.*['\"].*apps/\|from.*['\"].*src/" packages/ \
  --include="*.ts" --include="*.tsx" 2>/dev/null \
  | grep -v "node_modules\|\.storybook" | wc -l)
if [ "$count" -gt "0" ]; then
  echo "ERROR: Shared package importing from app code — breaks publishability."
  grep -rn "from.*apps/\|from.*src/" packages/ --include="*.ts" --include="*.tsx" \
    | grep -v "node_modules\|\.storybook"
  exit 1
fi
```
**Prerequisite:** `packages/` exists and contains no app imports.
**What it catches:** Package boundary violations that prevent publishing to GitHub Packages.
**Note:** Skip entirely if no `packages/` directory.

---

### Optional Checks (add when relevant)

#### O1. Storybook builds (add when packages/ui is active)
```yaml
- name: Storybook build
  run: cd packages/ui && pnpm build-storybook
```
**Prerequisite:** `packages/ui` exists with at least one story.
**What it catches:** Broken component stories — prevents fossil documentation.

#### O2. Convex type check (add when using Convex backend)
```yaml
- name: Convex type check
  run: npx convex dev --typecheck --once 2>&1 | tail -20
```
**Prerequisite:** Convex project configured locally.
**What it catches:** Convex schema/query type mismatches not caught by standard tsc.
**Note:** Run only when `convex/` files change using path filtering.

#### O3. Test coverage threshold (add when coverage is meaningful)
```yaml
- name: Test coverage
  run: pnpm vitest run --coverage
  # Fail if coverage drops below threshold
```
**Prerequisite:** Coverage baseline established and meaningful (>40% line coverage).
**What it catches:** New code added without tests.
**Note:** Don't add this check until the coverage number is stable — a moving threshold
just creates noise.

---

## Pre-commit Configuration

### Husky setup

```bash
# Install
pnpm add -D husky lint-staged

# Initialise
npx husky init
```

This creates `.husky/pre-commit`. Replace its contents with:

```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npx lint-staged
```

### lint-staged configuration

Add to `package.json`:

```json
{
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix --max-warnings 0",
      "prettier --write"
    ],
    "*.{json,md,css,yaml,yml}": [
      "prettier --write"
    ]
  }
}
```

**Do not add `tsc --noEmit` to lint-staged** unless your machine is fast.
TypeScript checks the whole project even when run on one file — it will be slow.
Put tsc in CI instead.

### Bypass for emergencies

Developers can bypass pre-commit with:
```bash
git commit --no-verify -m "emergency fix"
```
This is a safety valve, not a regular practice. If it's being used regularly,
the pre-commit checks are too slow or too strict.

---

## GitHub Actions Workflow Templates

### Minimal (safe starting point for any project)

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  quality:
    name: Quality checks
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup pnpm
        uses: pnpm/action-setup@v3
        with:
          version: 9

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Type check
        run: npx tsc --noEmit

      - name: Tests
        run: pnpm vitest run

      - name: No committed secrets
        run: |
          if git ls-files | grep -q "^\.env$"; then
            echo "ERROR: .env is tracked by git"
            exit 1
          fi
```

### Standard (recommended once baseline is clean)

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  quality:
    name: Quality checks
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup pnpm
        uses: pnpm/action-setup@v3
        with:
          version: 9

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Type check
        run: npx tsc --noEmit

      - name: Tests
        run: pnpm vitest run

      - name: Lint
        run: npx eslint src/ --ext .ts,.tsx --max-warnings 0

      - name: No committed secrets
        run: |
          if git ls-files | grep -q "^\.env$"; then
            echo "ERROR: .env is tracked by git"
            exit 1
          fi

      - name: Architectural checks
        run: |
          # No catch-any blocks
          count=$(grep -rn "catch.*: any" src/ --include="*.ts" --include="*.tsx" \
            | grep -v "_generated\|node_modules" | wc -l)
          if [ "$count" -gt "0" ]; then
            echo "ERROR: Found $count catch(err: any) blocks"
            grep -rn "catch.*: any" src/ --include="*.ts" --include="*.tsx" | grep -v "_generated"
            exit 1
          fi

          # Env vars in central config only
          count=$(grep -rn "import\.meta\.env\." src/ --include="*.ts" --include="*.tsx" \
            | grep -v "src/lib/env" | wc -l)
          if [ "$count" -gt "0" ]; then
            echo "ERROR: Env vars read outside src/lib/env.ts"
            grep -rn "import\.meta\.env\." src/ --include="*.ts" --include="*.tsx" | grep -v "src/lib/env"
            exit 1
          fi

          # No reverse dependencies
          count=$(grep -rn "from.*['\"].*pages/" src/utils/ src/lib/ src/stores/ \
            --include="*.ts" --include="*.tsx" 2>/dev/null | wc -l)
          if [ "$count" -gt "0" ]; then
            echo "ERROR: utils/lib/stores importing from pages/"
            exit 1
          fi

          echo "All architectural checks passed"
```

### Full (monorepo with Convex and packages/ui)

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  quality:
    name: Quality checks
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup pnpm
        uses: pnpm/action-setup@v3
        with:
          version: 9

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Type check (app)
        run: npx tsc --noEmit

      - name: Type check (packages/ui)
        run: cd packages/ui && npx tsc --noEmit

      - name: Tests
        run: pnpm vitest run

      - name: Lint
        run: npx eslint src/ --ext .ts,.tsx --max-warnings 0

      - name: No committed secrets
        run: |
          if git ls-files | grep -q "^\.env$"; then
            echo "ERROR: .env is tracked by git"
            exit 1
          fi

      - name: Circular dependency check
        run: npx madge src/ --circular --extensions ts,tsx

      - name: Architectural checks
        run: |
          echo "--- Check: no catch-any ---"
          count=$(grep -rn "catch.*: any" src/ convex/ \
            --include="*.ts" --include="*.tsx" \
            | grep -v "_generated\|node_modules" | wc -l)
          [ "$count" -eq "0" ] || { echo "FAIL: $count catch-any blocks"; exit 1; }

          echo "--- Check: env vars centralised ---"
          count=$(grep -rn "import\.meta\.env\." src/ --include="*.ts" --include="*.tsx" \
            | grep -v "src/lib/env" | wc -l)
          [ "$count" -eq "0" ] || { echo "FAIL: env vars outside src/lib/env.ts"; exit 1; }

          echo "--- Check: no reverse dependencies ---"
          count=$(grep -rn "from.*['\"].*pages/" src/utils/ src/lib/ src/stores/ \
            --include="*.ts" --include="*.tsx" 2>/dev/null | wc -l)
          [ "$count" -eq "0" ] || { echo "FAIL: utils importing from pages/"; exit 1; }

          echo "--- Check: stores not importing hooks/components ---"
          count=$(grep -rn "from.*['\"].*hooks/\|from.*['\"].*components/" src/stores/ \
            --include="*.ts" 2>/dev/null | wc -l)
          [ "$count" -eq "0" ] || { echo "FAIL: stores importing from hooks/components/"; exit 1; }

          echo "--- Check: packages/ui has no app imports ---"
          count=$(grep -rn "from.*['\"].*apps/\|from.*['\"].*\/src/" packages/ \
            --include="*.ts" --include="*.tsx" 2>/dev/null \
            | grep -v "node_modules\|\.storybook" | wc -l)
          [ "$count" -eq "0" ] || { echo "FAIL: package importing from app code"; exit 1; }

          echo "All architectural checks passed"

      - name: Storybook build
        run: cd packages/ui && pnpm build-storybook

  convex:
    name: Convex type check
    runs-on: ubuntu-latest
    if: |
      contains(github.event.head_commit.modified, 'convex/') ||
      github.event_name == 'pull_request'

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup pnpm
        uses: pnpm/action-setup@v3
        with:
          version: 9

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Convex type check
        env:
          CONVEX_DEPLOY_KEY: ${{ secrets.CONVEX_DEPLOY_KEY }}
        run: npx convex dev --typecheck --once 2>&1 | tail -30
```

---

## Implementation Plan

When this skill is invoked to set up CI/CD for a specific repo, produce an
implementation plan with this structure:

### Step 1: Assess current state

Run the discovery commands above. Produce a table:

| Check | Current state | Add now? | Deferred until |
|-------|--------------|----------|----------------|
| TypeScript | passes / N errors | yes / no | condition |
| Tests | passes / N failures | yes / no | condition |
| Lint | passes / N warnings | yes / no | condition |
| No .env | clean / tracked | yes / no | -- |
| catch-any | N instances | yes / no | zero instances |
| env centralised | N violations | yes / no | all centralised |
| circular deps | N cycles | yes / no | zero cycles |
| reverse deps | N violations | yes / no | zero violations |
| packages/ui clean | N violations / N/A | yes / no | package exists |
| Storybook builds | passes / N/A | yes / no | stories exist |

### Step 2: Install tooling

List exactly what needs installing based on what's missing:

```bash
# Pre-commit hooks (if not present)
pnpm add -D husky lint-staged

# Circular dep check (if not present)
pnpm add -D madge

# Prettier (if not present)
pnpm add -D prettier
```

### Step 3: Create config files

List every file to create with its full content:
- `.github/workflows/ci.yml` -- use the appropriate template above
- `.husky/pre-commit` -- lint-staged hook
- `package.json` additions -- lint-staged config, husky prepare script
- `.prettierrc` -- if not present
- `.prettierignore` -- if not present

### Step 4: Establish green baseline

Before wiring in any check, verify it passes:

```bash
npx tsc --noEmit                    # Must exit 0
pnpm vitest run                     # Must exit 0
npx eslint src/ --ext .ts,.tsx      # Fix or suppress before adding to CI
npx madge src/ --circular           # Resolve cycles or defer the check
```

Document any deferred checks and the condition that unblocks each one.

### Step 5: Commit in order

```bash
# 1. Tooling
git add package.json pnpm-lock.yaml
git commit -m "chore: add husky + lint-staged + madge"

# 2. Pre-commit hooks
git add .husky/ .prettierrc .prettierignore
git commit -m "chore: add pre-commit hooks (lint + format)"

# 3. CI workflow
git add .github/workflows/ci.yml
git commit -m "ci: add GitHub Actions workflow

Checks: tsc, vitest, eslint, no-.env, architectural enforcement.
Deferred: [list any deferred checks and why]"
```

---

## Evolving This Skill

As the codebase matures, add checks in this order:

| Maturity stage | Add this check |
|---------------|---------------|
| Baseline clean | Standard checks (S1-S4) |
| Zero catch-any | Architectural check A1 |
| Env centralised | Architectural check A2 |
| No reverse deps | Architectural check A3 |
| Stores clean | Architectural check A4 |
| Madge installed | Circular dep check A5 |
| packages/* exists | Package boundary check A6 |
| packages/ui has stories | Storybook build O1 |
| Convex backend | Convex typecheck O2 |
| Coverage >40% | Coverage threshold O3 |

**When a check is added, document in the commit message:**
- What the check enforces
- What the current count is (e.g. "0 catch-any blocks as of this commit")
- What condition would cause it to fail

This creates an audit trail of when each guardrail was added and why.

---

## Common Failure Modes

**"CI passes locally but fails in Actions"**
Usually a dependency issue. Check:
- `pnpm install --frozen-lockfile` vs `pnpm install` (lockfile drift)
- Node version mismatch (specify exact version in `setup-node`)
- Missing env vars (Actions needs secrets configured)

**"Pre-commit is too slow, developers bypass it"**
Remove tsc from lint-staged. Move to CI only. Keep pre-commit to format + lint only.

**"Architectural grep check has false positives"**
Tighten the grep pattern. Add specific exclusions with `| grep -v "known-exception"`.
Document the exception in a comment in the workflow file.

**"Convex typecheck hangs in CI"**
Convex `dev --typecheck` requires network access to Convex servers.
Add `CONVEX_DEPLOY_KEY` to GitHub secrets and ensure the job has the right env var.
Use `--once` flag to exit after check rather than watching.

**"pnpm workspace packages not resolving in CI"**
Ensure `pnpm install` is run from the repo root, not a subdirectory.
The `--frozen-lockfile` flag ensures the lockfile is respected.
Check that `pnpm-workspace.yaml` is committed.
