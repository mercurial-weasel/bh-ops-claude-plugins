---
name: code-quality
description: >
  Audit a codebase for architecture and code quality patterns that scale.
  Use when the user says "code quality", "audit this repo", "check architecture",
  "refactor assessment", "what needs fixing", "tech debt", "code review the repo",
  "architecture review", or any variation of reviewing a codebase for structural issues.
  Produces a scored report with specific file:line references and prioritised fixes.
---

# Code Quality Audit

Systematic architecture and code quality review. Checks 14 patterns extracted from
production-grade codebases. Produces a scored report with specific findings and
prioritised refactoring recommendations.

**This is an audit skill, not a fix skill.** Report findings. Do not modify code
unless the user explicitly asks for fixes after reviewing the report.

---

## How to Run

1. Read the project's CLAUDE.md (if present) to understand conventions already in place
2. Scan the top-level directory structure before diving into files — understand the shape before the detail
3. Run each check below against the codebase using the suggested commands
4. Score each dimension 1–10 based on evidence found
5. Produce the report in the output format below
6. **Save the report** to `docs/code-quality/YYYY-MM-DD-HH-MM-code-quality-audit.md` using the current date/time. Create the `docs/code-quality/` directory if it doesn't exist.

For each check: find 2–3 concrete examples (good or bad) with file:line references.
Skip checks that don't apply to the project's scale or language — mark as N/A with a reason.

**Suggested opening commands:**
```bash
# Understand the shape of the codebase
find . -type f -name "*.ts" -o -name "*.tsx" | wc -l
find . -type f -name "*.ts" -o -name "*.tsx" | head -60

# Find large files (god modules)
find src/ -name "*.ts" -o -name "*.tsx" | xargs wc -l | sort -rn | head -20

# Find any-type usage
grep -rn ": any\|as any\|catch (e)" src/ --include="*.ts" --include="*.tsx" | grep -v node_modules | grep -v _generated

# Find raw env var reads outside config files
grep -rn "process\.env\|import\.meta\.env" src/ --include="*.ts" --include="*.tsx" | grep -v "lib/env\|config"

# Find circular import candidates
grep -rn "from '\.\." src/ --include="*.ts" --include="*.tsx" | grep -v node_modules | grep -v test
```

---

## The 13 Checks

### 1. Dependency Direction

**What to check:** Do dependencies flow one way (leaves → core → app), or are there
circular imports and reverse dependencies? Can you draw the module graph as a DAG?

**Signs of quality:**
- Core business logic has zero dependency on infrastructure (DB, HTTP, platform SDKs)
- Infrastructure depends on core via interfaces, never the reverse
- No circular `import` chains between modules or packages
- Utility/lib packages do not import from page/component packages
- Shared packages (`packages/*`) import only from each other, never from `apps/*`

**Red flags:**
- Module A imports Module B which imports Module A
- A `utils/` file importing from `pages/` or `components/`
- A shared package depending on an application-level package
- `stores/` importing from `hooks/` or `components/`

**How to check:**
```bash
# Utils importing from pages (reverse dependency)
grep -rn "from.*pages/" src/utils/ src/lib/ src/stores/ --include="*.ts" --include="*.tsx"

# Shared packages importing from apps
grep -rn "from.*apps/" packages/ --include="*.ts" --include="*.tsx"

# Stores importing from hooks or components
grep -rn "from.*hooks/\|from.*components/" src/stores/ --include="*.ts"
```

---

### 2. Package Boundary Hygiene

**What to check:** If the repo has shared packages (monorepo or `packages/` structure),
are the package boundaries clean? Do packages stand alone, or do they secretly
reach into sibling packages or application code?

**Signs of quality:**
- Each package has its own `package.json` with explicit dependencies declared
- Packages export a clean public API via `index.ts` — internals not directly imported
- No package imports from `../../apps/something` (breaks publishability)
- Packages are in principle publishable to a registry (e.g. GitHub Packages) without modification
- `publishConfig` or equivalent present if publishing is intended

**Red flags:**
- Package importing from app-level code it doesn't declare as a dependency
- Consumers importing internal files directly (`@bh/schemas/src/geo-v1/atterberg`) rather than the barrel export
- No `index.ts` barrel — every file is a public surface
- `package.json` missing `"main"` or `"exports"` field

**How to check:**
```bash
# Packages reaching into app code
grep -rn "from '../../apps" packages/ --include="*.ts"

# Check each package has an index.ts
find packages/ -maxdepth 2 -name "index.ts"

# Check package.json exports fields
cat packages/*/package.json | grep -A3 '"exports"\|"main"\|"publishConfig"'
```

*Note: Mark N/A if the project has no `packages/` structure.*

---

### 3. Interface Segregation

**What to check:** Are interfaces narrow and focused, or are there "god interfaces"
that force implementers to provide methods they don't use?

**Signs of quality:**
- Consumers define the interface they need (dependency inversion)
- No interface exceeds ~10 methods
- Different consumers of the same module use different narrow interfaces
- Dependency injection via interface rather than concrete class

**Red flags:**
- One interface with 20+ methods that every adapter must implement
- Functions accepting a full class when they only use 2 methods on it
- `Partial<BigInterface>` used to avoid implementing unused methods
- Store types passed whole to utility functions that use 1 field

**Pattern to look for (good):**
```typescript
// Utility defines what IT needs, not what the store provides
interface HydrationTarget {
  setBudget: (data: BudgetState) => void;
  setRisk: (data: RiskState) => void;
}
// Caller wires real store at the boundary — utility stays testable
```

---

### 4. Type Safety at Boundaries

**What to check:** Are external data boundaries (API responses, file parsing, env vars,
JSON hydration) validated at entry, or does untyped data flow into the system?

**Signs of quality:**
- Zod / io-ts / valibot validation at all external entry points
- Branded/opaque types for commonly confused primitives (IDs, paths, amounts)
- Discriminated unions for results (`{ ok: true; value: T } | { ok: false; error: E }`)
- `catch (err: unknown)` with explicit narrowing — not `catch (err: any)`
- `JSON.parse()` always followed by schema validation before use

**Red flags:**
- `catch (err: any)` — bypasses TypeScript's type system on the most dangerous path
- Raw `JSON.parse()` without validation at hydration or API boundaries
- Excel/CSV row access via `row['field']` without shape validation
- `as SomeType` assertions on external data (casting, not validating)
- `v.any()` in a Convex schema for a field with a known shape

**How to check:**
```bash
# Find catch-any
grep -rn "catch.*: any" src/ convex/ --include="*.ts" --include="*.tsx" | grep -v _generated

# Find raw JSON.parse without nearby validation
grep -rn "JSON\.parse" src/ --include="*.ts" --include="*.tsx"

# Find as-any assertions
grep -rn " as any" src/ --include="*.ts" --include="*.tsx" | grep -v node_modules
```

---

### 5. Error Classification

**What to check:** Does the codebase distinguish between error types that require
different handling (retry vs fail vs notify user), or is everything `catch (e) { log(e) }`?

**Signs of quality:**
- Explicit error taxonomy (FATAL / TRANSIENT / UNKNOWN or domain-specific codes)
- Fatal errors (auth, permission) are never retried
- Transient errors (timeout, rate limit) have retry with backoff
- User-facing errors are classified and mapped to friendly messages
- A shared `AppError` or equivalent carries code + retryable + userFacing flags

**Red flags:**
- Generic `catch` blocks that log and swallow without classification
- Retry logic that retries authentication failures
- Raw SDK/database error messages surfaced to users
- No distinction between "bug in our code" and "external service unavailable"
- `toAppError()` exists but is not consistently used across catch blocks

**How to check:**
```bash
# Find console.error without toAppError or equivalent
grep -rn "console\.error" src/hooks/ src/components/ --include="*.ts" --include="*.tsx"

# Find swallowing catch blocks (catch with no rethrow or error surface)
grep -rn "catch" src/ --include="*.ts" | grep -v "toAppError\|AppError\|console"
```

---

### 6. State Machine Discipline

**What to check:** Are stateful entities (sessions, orders, workflows, upload batches)
managed through explicit state transitions, or can state be mutated arbitrarily?

**Signs of quality:**
- Explicit status enum with valid transitions defined
- State transitions create audit records (who, when, why)
- Invalid transitions throw or return an error — not silently ignored
- Status values are a closed set (enum or `z.enum()`), not open strings

**Red flags:**
- Status field updated via raw mutation with no transition validation
- Multiple uncoordinated places in code that set `status = 'completed'`
- No record of WHY a state changed
- Status typed as `string` rather than a union of known values

---

### 7. Test Quality and Distribution

**What to check:** Are tests testing the right things at the right level? Do they
run independently, or do they leak state into each other?

**Signs of quality:**
- Unit tests cover pure functions and business logic (not just happy paths)
- Tests for error paths and edge cases, not just success paths
- Each test file can run in isolation
- Mocked modules are scoped — no global mock state persisting between files
- Store tests reset state in `beforeEach`

**Red flags:**
- Tests only cover utility functions — business logic untested
- No tests for error paths (the most dangerous code)
- Tests that fail when run individually but pass in suite (order dependency)
- `beforeAll` setting up state consumed by tests in other files
- Test files importing from `../stores/` without resetting state

**How to check:**
```bash
# Count test files vs source files
find src/__tests__ -name "*.test.ts" | wc -l
find src/ -name "*.ts" -not -path "*__tests__*" -not -path "*node_modules*" | wc -l

# Check for beforeEach resets in store tests
grep -rn "beforeEach\|setState" src/__tests__/ --include="*.test.ts"
```

---

### 8. Fail-Fast at System Boundaries

**What to check:** Does the system validate inputs early and reject bad data
before it propagates, or does it fail deep in the stack with confusing errors?

**Signs of quality:**
- API routes validate request body/params before hitting business logic
- Config/env vars validated at startup in a single location (not when first used)
- File parsing (CSV, Excel, AGS) validates row shape before processing
- Constructor or factory validation — reject invalid state at creation time
- Missing required config fails loud at boot, not silently at first use

**Red flags:**
- Env var read deep in a business logic function, crashing at runtime if missing
- File rows accessed by column name without checking the column exists
- `process.env.X` scattered through business logic rather than centralised
- Validation that happens after side effects have already started

**How to check:**
```bash
# Raw env var reads outside a central config/env file
grep -rn "process\.env\.\|import\.meta\.env\." src/ convex/ --include="*.ts" --include="*.tsx" \
  | grep -v "lib/env\|env\.ts\|config\.ts\|node_modules\|_generated"
```

---

### 9. Observable-Only Side Effects

**What to check:** Are non-critical side effects (logging, metrics, analytics, events)
isolated so their failure never blocks the primary operation?

**Signs of quality:**
- Event emission is fire-and-forget with internal error catching
- Logging failures never propagate to callers
- Analytics/metrics calls wrapped in try-catch with their own error boundary
- `await` is not used on non-critical side effects in the critical path

**Red flags:**
- `await logEvent(...)` in the critical path without try/catch
- Analytics failure crashes a user-facing operation
- Side-effect errors surfaced to users as if they were domain errors

---

### 10. Graceful Degradation

**What to check:** When a dependency is unavailable, does the system degrade
gracefully or crash entirely?

**Signs of quality:**
- Multi-layer fallback chains (primary → fallback → safe default)
- Partial results returned when some data sources fail
- Clear user notification of degraded state without exposing internals
- Timeouts on all external calls (no open-ended awaits)
- AI/LLM calls have explicit timeout + user-friendly timeout message

**Red flags:**
- Entire page fails because one non-critical service is down
- No timeouts on external HTTP or AI API calls
- "All or nothing" responses when partial data would be useful
- AI thinking spinner with no timeout or escape hatch

---

### 11. Configuration Hierarchy

**What to check:** Is configuration layered sensibly (defaults < env vars < runtime),
or scattered across env vars, config files, and hardcoded values?

**Signs of quality:**
- Single `src/lib/env.ts` (or equivalent) as the only place env vars are read
- Clear precedence: hardcoded defaults → config file → env vars
- Config validated at startup with clear, actionable error messages
- All config values documented (ideally in `.env.example`)

**Red flags:**
- `process.env.X` or `import.meta.env.X` scattered throughout business logic
- Same setting configurable in multiple places with unclear precedence
- No default values (missing env var = crash at runtime, often far from the read)
- `.env` committed to version control

**How to check:**
```bash
# Env vars outside the central config file
grep -rn "import\.meta\.env\." src/ --include="*.ts" --include="*.tsx" | grep -v "src/lib/env"

# Check .env is gitignored
git ls-files .env
```

---

### 12. Module Cohesion

**What to check:** Does each file/module/package have a single clear purpose,
or are there god modules mixing concerns?

**Signs of quality:**
- File names describe what they do (`snapshotSerializer.ts` not `utils.ts`)
- Functions in a module share the same domain concept
- You can describe what a module does in one sentence
- Stores hold state and actions only — no derived data computation
- Page components handle rendering only — computation extracted to utils

**Red flags:**
- `utils.ts` or `helpers.ts` over 200 lines with unrelated functions
- A single store managing 3+ unrelated concerns (schedule metadata + comments + discrepancies)
- Page components containing 100+ line pure computation functions
- `hooks/` containing what are effectively stores (no React lifecycle dependency)

**How to check:**
```bash
# Large files
find src/ -name "*.ts" -o -name "*.tsx" | xargs wc -l 2>/dev/null | sort -rn | head -15

# Stores with many concerns
wc -l src/stores/*.ts | sort -rn | head -10
```

---

### 13. Cleanup and Resource Management

**What to check:** Are resources (connections, file handles, object URLs, background
processes, timers) properly cleaned up, including on error paths?

**Signs of quality:**
- `URL.createObjectURL()` always paired with `URL.revokeObjectURL()` after use
- `setTimeout`/`setInterval` cleared in cleanup or `finally` blocks
- Zustand subscriptions unsubscribed in `useEffect` cleanup
- AbortController used for cancellable fetch/API calls
- Temporary resources have TTL or explicit cleanup

**Red flags:**
- Object URLs created but never revoked (memory leak on repeated use)
- Timers set in effects without cleanup return function
- Background processes or intervals with no kill mechanism
- Cleanup that throws, preventing subsequent cleanup steps

**How to check:**
```bash
# Object URL creation without revoke nearby
grep -rn "createObjectURL" src/ --include="*.ts" --include="*.tsx"
grep -rn "revokeObjectURL" src/ --include="*.ts" --include="*.tsx"

# useEffect without cleanup
grep -rn "useEffect" src/ --include="*.tsx" -A 10 | grep -v "return () =>"
```

---

### 14. Design System and Visual Consistency

**What to check:** Is there a shared visual language across the product surfaces
(portal, dropsite, client-facing tools), or does each app accumulate its own
ad-hoc colour tokens, spacing scales, and component variants?

**This check has two tiers depending on maturity:**

**Tier 1 — No shared UI package yet (early stage)**

The question is whether the foundations are in place to extract one later without
a rewrite. Signs you're set up well:
- Tailwind config uses a consistent custom colour/spacing scale rather than raw values
- Components are structured in a way that could be moved to `packages/ui` (no app-specific imports baked in)
- No hardcoded hex values scattered through component files outside the Tailwind config
- `.storybook/` exists even if dormant — signals intent to document components

Signs of drift beginning:
- Two apps with separate Tailwind configs that have diverged colour tokens
- Components duplicated across apps with slight variations (different padding, different font sizes)
- No shared `packages/ui` despite multiple app surfaces existing

**Tier 2 — packages/ui exists**

- Components exported via a clean barrel (`packages/ui/src/index.ts`)
- Storybook stories exist for every exported component, showing all meaningful states
- Stories are current — not fossil documentation from a previous design iteration
- Consuming apps use package components rather than re-implementing locally
- Design tokens (colours, spacing, typography) defined once in `packages/ui/tokens.ts` and imported everywhere

**Red flags (either tier):**
- Hardcoded hex values in component files (`className="text-[#2D6BE4]"`)
- The same Button or Card component implemented differently in two apps
- Storybook present but with 0–1 active stories (fossil state)
- `packages/ui` exists but consuming apps bypass it and implement components locally

**How to check:**
```bash
# Hardcoded hex colours outside tailwind config
grep -rn "#[0-9a-fA-F]\{3,6\}" src/ apps/ --include="*.tsx" --include="*.ts" \
  | grep -v "tailwind.config\|tokens\|node_modules"

# Duplicate component names across apps
find apps/ -name "Button.tsx" -o -name "Card.tsx" -o -name "Footer.tsx" 2>/dev/null

# Check Storybook story count and recency
find . -name "*.stories.tsx" -o -name "*.stories.ts" 2>/dev/null
git log --oneline -- "**/*.stories.*" | head -5

# Check packages/ui exists and has an index
ls packages/ui/src/index.ts 2>/dev/null && echo "exists" || echo "no packages/ui yet"
```

**Scoring guide for this check:**
- **8–10**: `packages/ui` with current stories, tokens defined once, no duplication
- **6–7**: Consistent Tailwind config, components extractable, Storybook dormant but present
- **4–5**: Some token consistency but components duplicated or diverging across apps
- **2–3**: Ad-hoc styling, hardcoded values, no shared foundation
- **1**: Multiple apps with visually inconsistent UI and no path to convergence

*Note: Score at Tier 1 ceiling (max 7) if `packages/ui` does not yet exist, regardless
of how good the Tailwind config is. The ceiling reflects structural readiness, not
current quality.*

---

## Output Format

```markdown
# Code Quality Audit: {repo name}

**Date:** {date}
**Auditor:** Claude Code
**Scope:** {what was reviewed — full repo / specific packages / recent changes}
**Codebase size:** {approx file count and line count}

---

## Scores

| # | Dimension | Score | Key Finding |
|---|-----------|-------|-------------|
| 1 | Dependency Direction | X/10 | one-line summary |
| 2 | Package Boundary Hygiene | X/10 | one-line summary |
| 3 | Interface Segregation | X/10 | one-line summary |
| 4 | Type Safety at Boundaries | X/10 | one-line summary |
| 5 | Error Classification | X/10 | one-line summary |
| 6 | State Machine Discipline | X/10 | one-line summary |
| 7 | Test Quality & Distribution | X/10 | one-line summary |
| 8 | Fail-Fast at Boundaries | X/10 | one-line summary |
| 9 | Observable-Only Side Effects | X/10 | one-line summary |
| 10 | Graceful Degradation | X/10 | one-line summary |
| 11 | Configuration Hierarchy | X/10 | one-line summary |
| 12 | Module Cohesion | X/10 | one-line summary |
| 13 | Cleanup & Resources | X/10 | one-line summary |
| 14 | Design System & Visual Consistency | X/10 | one-line summary |

**Overall: {average}/10**
**Previous score (if applicable):** {X/10 — note trajectory}

---

## Top Findings

### Critical (fix before next feature)
1. **{short label}** — `file:line` — {why this matters, what goes wrong if left}
2. ...

### Important (fix in next refactor pass)
1. **{short label}** — `file:line` — {specific impact}
2. ...

### Minor (fix opportunistically)
1. **{short label}** — `file:line` — {low-priority note}
2. ...

---

## Positive Patterns Worth Preserving
1. **{pattern name}** — `file:line` — {why it's good, what it enables}
2. ...

---

## Recommended Refactoring Order

Ordered by ROI: highest impact relative to effort first.

| Priority | Change | Files affected | Scope | Rationale |
|----------|--------|---------------|-------|-----------|
| 1 | {change} | {files} | small/medium/large | {why now} |
| 2 | ... | | | |

---

## Known Gaps (out of scope / accepted debt)

1. **{gap}** — {why accepted, what would trigger revisiting it}
```

---

## Historical Review (Post-Report Step)

After writing the initial report, check for past audit reports in the project's `docs/code-quality/` folder:

```bash
ls docs/code-quality/*.md 2>/dev/null | sort
```

If past reports exist:

1. **Read each previous report** (most recent first, up to 3 prior audits)
2. **Add a Trajectory section** to the current report, after the Scores table:

```markdown
## Trajectory

| Date | Overall | Notable Changes |
|------|---------|-----------------|
| {date} | {score}/10 | {1-line summary of what changed} |
| {date} | {score}/10 | {1-line summary} |

**Trend:** {Improving / Stable / Declining} — {one sentence explaining the direction}
```

3. **Update individual check scores** with trajectory notes where relevant — e.g., if Check 5 (Error Classification) improved from 5/10 to 8/10 between audits, note this in the Key Finding column: `"8/10 (was 5/10) — AppError now consistently adopted"`
4. **Flag regressions** — if any check scored lower than the previous audit, call it out in the Critical findings section with a note like: `"Regression from {X}/10 → {Y}/10 since {date} audit"`
5. **Validate prior recommendations** — check whether the previous audit's "Recommended Refactoring Order" items were actually addressed. Note which were completed, which are still open, and whether any new issues appeared in areas that were previously clean.

If no past reports exist, note in the report header: `**Previous score:** N/A (first audit)`

This step runs **after** the initial report is written and saved. Update the saved report file in-place with the trajectory data.

---

## Scoring Guide

| Score | Meaning |
|-------|---------|
| 9–10 | Exemplary. Could be used as a teaching reference. |
| 7–8 | Solid. Minor issues, patterns are generally correct. |
| 5–6 | Mixed. Some good patterns but significant gaps. |
| 3–4 | Weak. Systematic issues that will compound as the codebase grows. |
| 1–2 | Critical. Fundamental patterns missing or actively harmful. |

Score based on what you actually find, not what documentation claims.
Evidence over assertions. A 5/10 with accurate findings is more useful than a flattering 8/10.

---

## Important Notes for the Auditor

- **Be specific.** Every finding needs a `file:line` reference. "Error handling could be better" is useless.
- **Be honest.** Don't round up scores to avoid discomfort.
- **Be proportionate.** A 500-line script doesn't need the same scrutiny as a 50K-line platform.
- **Note trajectory.** If a previous audit score exists, note whether the codebase is improving.
- **Highlight what's good.** Patterns worth preserving are as important as patterns to fix.
- **Mark N/A clearly.** A static site doesn't need error classification review — say so and move on.
- **Check 2 (Package Boundary Hygiene)** — skip entirely if the repo has no `packages/` structure.
- **Check 14 (Design System)** — score at Tier 1 ceiling (max 7/10) if `packages/ui` does not exist. A single-app repo with no multi-surface deployment can score max 6/10 on this check.