# Obsidian Markdown File Generation — Full Reference

## 1. File Naming

- Use **kebab-case** for filenames: `capital-planning-framework.md`
- No spaces, no special characters beyond hyphens
- Keep names concise but descriptive (3–6 words max)
- Prefix with a category if the vault uses flat structure: `ref-capital-planning-framework.md`

---

## 2. YAML Frontmatter

Every file **must** begin with a YAML frontmatter block delimited by `---`.

### 2.1 Basic Structure

```yaml
---
title: "Capital Planning Framework"
aliases:
  - "CPF"
  - "Capital Framework"
type: note
status: draft
tags:
  - capital-planning
  - frameworks
  - governance
created: 2026-03-21
updated: 2026-03-21
---
```

### 2.2 Required Fields

| Field       | Type       | Description                                                        |
|-------------|------------|--------------------------------------------------------------------|
| `title`     | string     | Human-readable title. Wrap in quotes if it contains colons or special chars. |
| `type`      | string     | The note's archetype (see §2.4 below).                             |
| `status`    | string     | Lifecycle state: `draft`, `active`, `review`, `archived`, `seed`.  |
| `tags`      | list       | Lowercase, hyphenated. No `#` prefix — Obsidian adds it.          |
| `created`   | date       | ISO 8601 date: `YYYY-MM-DD`.                                      |
| `updated`   | date       | ISO 8601 date. Update this every time the file is modified.        |

### 2.3 Optional but Recommended Fields

| Field         | Type       | Description                                                      |
|---------------|------------|------------------------------------------------------------------|
| `aliases`     | list       | Alternative names for linking. Obsidian resolves these in `[[]]`.|
| `summary`     | string     | One-line description. Useful for Dataview tables and hover previews. |
| `parent`      | string     | Wiki-link to a parent note: `"[[programme-governance]]"`.        |
| `project`     | string     | Associated project or workstream.                                |
| `source`      | string     | Origin URL, document ref, or person.                             |
| `author`      | string     | Who created this content.                                        |
| `domain`      | string     | Knowledge domain: `strategy`, `technical`, `operations`, `personal`. |
| `priority`    | string     | `high`, `medium`, `low` — useful for task/action notes.          |
| `due`         | date       | Due date for actionable items.                                   |
| `cssclass`    | string     | Custom CSS class for per-note styling.                           |

### 2.4 Note Types (the `type` field)

| Type           | Use Case                                                    |
|----------------|-------------------------------------------------------------|
| `note`         | General knowledge capture, evergreen notes                  |
| `reference`    | External material, articles, book notes, specs              |
| `meeting`      | Meeting notes with attendees, decisions, actions            |
| `decision`     | Decision record (context, options, outcome)                 |
| `project`      | Project overview / index note                               |
| `person`       | Contact or stakeholder profile                              |
| `log`          | Daily log, journal, or retrospective                        |
| `template`     | Obsidian template file                                      |
| `moc`          | Map of Content — an index that links related notes          |
| `action`       | A discrete task or open loop                                |
| `framework`    | A reusable model, methodology, or mental model              |
| `artefact`     | A produced deliverable (report, presentation, proposal)     |

### 2.5 YAML Formatting Rules

- **Always quote strings** that contain colons, special characters, or start with `[` or `{`.
- **Dates must be unquoted** and in `YYYY-MM-DD` format for Obsidian/Dataview to parse them as dates.
- **Tags are a YAML list**, not a comma-separated string:
  ```yaml
  # CORRECT
  tags:
    - capital-planning
    - governance

  # WRONG
  tags: capital-planning, governance
  ```
- **Do not use tabs** — YAML requires spaces (2-space indent is standard).
- **No trailing spaces** after values.
- **Boolean values**: use `true` / `false` (lowercase, unquoted).
- **Null values**: use `null` or omit the field entirely — never leave a field with an empty value like `source:` with nothing after it.

---

## 3. Document Body Structure

### 3.1 Heading Hierarchy

- **H1 (`#`) is reserved** — Obsidian uses the filename or `title` frontmatter as H1. Start body content at **H2 (`##`)**.
- Maintain strict hierarchy: never skip levels (e.g., don't jump from `##` to `####`).

```markdown
## Overview

Brief context paragraph.

## Key Principles

### Principle 1: Adaptive Governance

Details here.

### Principle 2: Data-Driven Decisions

Details here.

## Related

- [[programme-governance]]
- [[decision-engine-overview]]
```

### 3.2 Linking

- Use **wiki-links** (`[[note-name]]`) for internal references, not standard markdown links.
- Use **aliased links** when the display text should differ: `[[capital-planning-framework|the framework]]`.
- Use **heading links** for precision: `[[note-name#Section Heading]]`.
- **External URLs** use standard markdown: `[Display Text](https://example.com)`.

### 3.3 Tags in Body

- Tags can also appear inline in the body as `#tag-name`.
- Keep them consistent with frontmatter tags — don't introduce tags in-body that aren't also in frontmatter.

### 3.4 Callouts

```markdown
> [!note] Context
> This framework applies to portfolios exceeding $1B in capital value.

> [!warning] Governance Gap
> No formal decision authority matrix exists below ELT level.

> [!tip] Quick Win
> Start with the top 10 programmes by value for initial rollout.
```

Supported callout types: `note`, `tip`, `warning`, `danger`, `info`, `question`, `success`, `failure`, `bug`, `example`, `quote`, `abstract`, `todo`.

### 3.5 Code Blocks

Use fenced code blocks with language identifiers:

````markdown
```typescript
const result = await ctx.db.query("programmes").collect();
```
````

### 3.6 Tables

Standard markdown tables. Keep them simple — complex data belongs in linked notes or external files.

### 3.7 Task Lists

```markdown
- [ ] Draft governance framework
- [x] Confirm stakeholder list
- [ ] Schedule ELT review #action
```

---

## 4. Special Note Templates

### 4.1 Meeting Note

```yaml
---
title: "Weekly Sync — Platform Team"
type: meeting
status: active
tags:
  - northwind
  - meeting
created: 2026-03-21
updated: 2026-03-21
attendees:
  - "[[dave-hall]]"
  - "[[alex-stanton]]"
---
```

Body sections: `## Agenda`, `## Discussion`, `## Decisions`, `## Actions`

### 4.2 Decision Record

```yaml
---
title: "DEC-2026-012: Platform Hosting Model"
type: decision
status: active
tags:
  - architecture
  - decisions
created: 2026-03-21
updated: 2026-03-21
decision_date: 2026-03-21
decision_maker: "[[dave-hall]]"
---
```

Body sections: `## Context`, `## Options Considered`, `## Decision`, `## Consequences`

### 4.3 Person / Stakeholder Note

```yaml
---
title: "Alex Stanton"
type: person
status: active
tags:
  - northwind
  - stakeholder
aliases:
  - "MC"
created: 2026-03-21
updated: 2026-03-21
organisation: "Northwind Utilities"
role: "Client Champion"
---
```

Body sections: `## Context`, `## Key Interactions`, `## Notes`

---

## 5. Anti-Patterns to Avoid

| Don't                                         | Do Instead                                      |
|-----------------------------------------------|------------------------------------------------|
| Use H1 in the body                            | Start at H2                                     |
| Put `#` in frontmatter tags                   | Use bare words: `capital-planning`              |
| Use spaces in tags                            | Use hyphens: `open-loop` not `open loop`        |
| Leave frontmatter fields empty                | Omit the field or use `null`                    |
| Use standard markdown links for internal refs | Use `[[wiki-links]]`                            |
| Create massive monolithic notes               | Split into atomic notes and link them           |
| Duplicate information across notes            | Link to a single source of truth                |
| Use inconsistent tag naming                   | Maintain a tag taxonomy and stick to it         |
| Nest YAML lists incorrectly                   | Use 2-space indented `- item` format            |
| Use tabs in YAML                              | Use spaces only                                 |

---

## 6. Dataview Compatibility Tips

- Keep field names **lowercase** and **single-word or hyphenated** (e.g., `decision_date`).
- Use **ISO dates** (`YYYY-MM-DD`) so Dataview can sort and filter.
- Use **wiki-links in frontmatter** (quoted) for relational queries: `parent: "[[parent-note]]"`.
- Use **consistent enum values** for `status`, `type`, `priority` — Dataview groups by exact string match.
