---
name: spec-writer
description: >
  Generate a comprehensive technical specification document optimised for Claude Code agentic execution.
  Use this skill whenever a user wants to spec out a feature, system, or product — including phrases like
  "write a spec", "create a spec", "spec this out", "I want to build X", "document this feature",
  "create a technical plan", "plan this system", or any time they describe something they want built
  and need a structured implementation plan. Also trigger when a user describes an architecture or
  workflow and asks how to structure it for an agent or developer. Always use this skill before
  starting any significant build — it produces a single structured document covering architecture,
  data models, API, frontend components, parallel agent tasks, and acceptance criteria.
---

# Spec Writer

Produces a single comprehensive specification document structured for parallel execution by Claude Code.

---

## Inputs to Gather

Before writing the spec, extract from the conversation or ask the user for:

1. **User story / brief description** — what does this feature/system do and for whom?
2. **Tech stack** — frontend framework, backend, database, auth, hosting (ask if not stated)
3. **Existing codebase context** — any relevant schema, components, or patterns already in place
4. **Scope boundaries** — what is explicitly OUT of scope for this spec?

If the user has provided a description, extract as much as possible from it before asking questions. Ask only for what's missing.

---

## Output Format

Produce a **single markdown document** with the following sections in order:

---

### 1. Overview
- One paragraph: what this system/feature does, who uses it, and why it exists
- Tech stack declaration (frontend, backend, DB, auth, infra)
- Key constraints or assumptions

---

### 2. Architecture Overview
- High-level diagram described in text or ASCII
- How the major layers connect (UI → API → DB, event flows, external services)
- Data flow narrative: trace a key user action end-to-end

---

### 3. Data Models / Schema
For each entity:
```
Entity: <Name>
Table/Collection: <name>
Fields:
  - field_name: type | description | constraints
Indexes: list any non-primary indexes
Relationships: foreign keys or references
```
Include all entities. If using Convex, write as Convex schema syntax. If using Prisma, write as Prisma schema. Match the project's actual ORM/DB.

---

### 4. API / Backend Functions
For each endpoint or backend function:
```
Function: <name>
Type: query | mutation | action | REST GET/POST/etc.
Input: { field: type }
Output: { field: type }
Auth: required role or none
Description: what it does
Side effects: any writes, emails, webhooks triggered
```
Group by domain (e.g. "Bid Functions", "User Functions").

---

### 5. Frontend Components
For each significant component:
```
Component: <Name>
Route/Location: <path or parent component>
Props: { field: type }
State: key local state variables
Data fetching: which API calls / queries it uses
User interactions: what the user can do
```
Note any shared/reusable components. Include page-level components and key sub-components.

---

### 6. JSON Schemas (if applicable)
If the system uses structured JSON as a data contract (e.g. document section schemas, AI output schemas), define them here:
```json
{
  "type": "object",
  "properties": {
    "field": { "type": "string", "description": "..." }
  },
  "required": ["field"]
}
```
Include one schema block per distinct JSON structure.

---

### 7. Agent Task Breakdown

Break the full build into parallel workstreams. Each workstream should be independently executable with no blocking dependency on other workstreams (unless explicitly noted).

Format:
```
## Workstream A: <Name>
Depends on: none | Workstream X (describe what specifically)
Tasks:
  1. <Specific, atomic task with clear done condition>
  2. ...
Files to create/modify: list key files
Done when: <acceptance statement>

## Workstream B: <Name>
...
```

Guidelines for task breakdown:
- Each task should be completable in one Claude Code session
- Tasks must reference specific file names, function names, or component names from earlier sections
- Avoid vague tasks like "implement the feature" — every task must be atomic and verifiable
- Data model workstream always runs first (other workstreams depend on it)
- UI and API workstreams can run in parallel after data model is done
- Integration/wiring workstream runs last

---

### 8. Acceptance Criteria

For each major capability, a testable pass/fail statement:
```
[ ] <Capability>: <specific observable behaviour that proves it works>
```

Group by workstream. Cover happy path, key error states, and edge cases.

---

## Writing Guidelines

- Be specific. Use exact field names, function names, component names throughout.
- Be consistent. A field named `rfpId` in the schema should be `rfpId` everywhere.
- Write for Claude Code, not a human reader. Assume the agent will execute tasks sequentially within a workstream and needs no hand-holding — but does need precision.
- If the user's brief is ambiguous, make a reasonable assumption and note it clearly with `> Assumption: ...`
- If scope is unclear, err on the side of a tighter scope and note what was deferred.
- Total document length: aim for 600–1200 lines. Longer is fine for complex systems.

---

## Process

1. Read all available context from the conversation
2. Ask only for missing critical inputs (stack, scope) — one question block maximum
3. Write the full spec in one pass
4. After writing, summarise: number of workstreams, estimated parallelism, any key assumptions made
5. Offer to refine any section or adjust scope
