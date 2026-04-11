---
description: Write a full technical specification from a brainstorm design
argument-hint: <feature name>
---

# Write Spec

## Your Mission

Read the approved design from `$ARTIFACTS_DIR/brainstorm-design.md` and write a complete technical specification.

## Requirements

The spec must be implementable by an engineer who was NOT part of the brainstorm. Every decision must be explicit — no "use your judgment" or "as appropriate."

## Spec Structure

1. **Overview** — what this is, why it exists, one paragraph
2. **Goals and Non-Goals** — explicit scope boundaries
3. **Architecture** — components, data flow, key interfaces
4. **Detailed Design** — every module/function/endpoint with:
   - Inputs and outputs (exact types)
   - Behavior (what it does, step by step)
   - Error handling (what can go wrong, what happens)
5. **Data Model** — schemas, types, validation rules
6. **Testing Strategy** — what to test, how, acceptance criteria
7. **Open Questions** — anything unresolved (should be minimal)

## Quality Checks

Before writing output, scan your spec for:
- Placeholder text (incomplete markers, filler phrases) — replace with actual content
- Ambiguous language ("should", "might", "could") — make it definitive
- Missing error handling — every operation needs a failure mode
- Unstated assumptions — make them explicit

## Output

Write the complete spec to `$ARTIFACTS_DIR/spec.md`.
