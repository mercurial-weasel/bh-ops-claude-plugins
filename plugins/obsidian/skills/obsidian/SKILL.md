---
name: obsidian
description: >
  Create well-structured Obsidian notes with rich YAML frontmatter, proper markdown formatting,
  internal links, tags, callouts, and organized folder structures. Uses the Obsidian MCP tools
  to write directly to the user's vault.

  Use this skill whenever the user asks to: create an Obsidian note, write notes, build a knowledge base,
  create a MOC (Map of Content), set up a vault structure, organize notes, create templates,
  write meeting notes, create a daily note, build a project tracker, or any request involving
  creating or organizing content in Obsidian. Also trigger when users mention "vault", "note-taking",
  "PKM" (personal knowledge management), or want to capture/document information in a structured way,
  even if they don't explicitly say "Obsidian".
---

# Obsidian Note Creator

You create well-structured, beautifully formatted Obsidian notes using the Obsidian MCP tools. Every note you produce should feel like it was crafted by an experienced PKM practitioner — with thoughtful frontmatter, clean hierarchy, and useful metadata.

## Available Tools

You have these Obsidian MCP tools at your disposal:

| Tool | Purpose |
|------|---------|
| `mcp__obsidian__write_note` | Create or overwrite a note (supports frontmatter object + content) |
| `mcp__obsidian__read_note` | Read an existing note |
| `mcp__obsidian__read_multiple_notes` | Batch-read up to 10 notes |
| `mcp__obsidian__patch_note` | Surgically update part of a note |
| `mcp__obsidian__update_frontmatter` | Update frontmatter without touching content |
| `mcp__obsidian__manage_tags` | Add, remove, or list tags |
| `mcp__obsidian__search_notes` | Search vault by content or frontmatter |
| `mcp__obsidian__list_directory` | Browse vault folder structure |
| `mcp__obsidian__get_vault_stats` | Get vault statistics |
| `mcp__obsidian__move_note` | Move or rename notes |
| `mcp__obsidian__get_frontmatter` | Read just the frontmatter |
| `mcp__obsidian__get_notes_info` | Get metadata for multiple notes |
| `mcp__obsidian__delete_note` | Delete a note (requires path confirmation) |

## Workflow

### Step 1: Understand the vault

Before creating notes, quickly orient yourself:

1. **Check vault structure** — call `mcp__obsidian__list_directory` on `/` to see existing folders and conventions
2. **Check recent notes** — call `mcp__obsidian__get_vault_stats` to see what's been worked on recently
3. **Read a few existing notes** if any exist, to match the user's existing style and frontmatter conventions

This context helps you place new notes in sensible locations and stay consistent with what's already there. If the vault is empty or new, you have freedom to establish good conventions from scratch.

### Step 2: Plan the note structure

Before writing, decide:

1. **Where it goes** — pick an appropriate folder path (create folders implicitly by writing to them)
2. **What frontmatter it needs** — choose properties that add real value for this note type
3. **What the content structure looks like** — headings, sections, callouts, links
4. **What links to create** — internal links to related notes (existing or future)

### Step 3: Write the note(s)

Use `mcp__obsidian__write_note` with both the `frontmatter` object and `content` string. The tool handles YAML serialization — pass frontmatter as a JSON object, not as a YAML string inside content.

## Frontmatter Guidelines

Every note gets frontmatter. Choose properties that are genuinely useful — not just filler. Here are the core properties by note type:

### Universal Properties (use on every note)

```yaml
---
created: 2026-03-06
tags:
  - topic/subtopic
type: note
---
```

- **created** — date of creation (YYYY-MM-DD)
- **tags** — hierarchical tags using `/` separators (e.g., `project/agora`, `area/health`, `type/meeting`)
- **type** — the note's category (see Note Types below)

### Extended Properties (use when relevant)

| Property | Use when | Example |
|----------|----------|---------|
| `aliases` | Note has alternate names | `["PKM", "Personal Knowledge Management"]` |
| `status` | Note is part of a workflow | `draft`, `in-progress`, `complete`, `archived` |
| `project` | Note belongs to a project | `"Agora Orchestrator"` |
| `source` | Content came from somewhere | `"https://example.com"` or `"Book: Thinking Fast and Slow"` |
| `author` | Attributing content | `"Richard Feynman"` |
| `related` | Explicit related notes | `["[[Note A]]", "[[Note B]]"]` |
| `rating` | For reviews/assessments | `4` (out of 5) |
| `due` | Has a deadline | `2026-04-01` |
| `updated` | Track last modification | `2026-03-06` |
| `cssclasses` | Custom styling | `["wide-page", "kanban"]` |
| `publish` | Obsidian Publish flag | `true` or `false` |

Do NOT add properties that will be empty or meaningless. A note about a recipe doesn't need `status` or `due`. A quick idea doesn't need `author` or `source`. Less metadata done well beats more metadata done poorly.

## Note Types

Use the `type` frontmatter property. Common types:

| Type | Description | Key extra properties |
|------|-------------|---------------------|
| `note` | General knowledge note | — |
| `moc` | Map of Content (index note) | — |
| `daily` | Daily note | — |
| `meeting` | Meeting notes | `attendees`, `project` |
| `project` | Project overview | `status`, `due` |
| `reference` | Reference material | `source`, `author` |
| `person` | Info about a person | `role`, `company` |
| `book` | Book notes/review | `author`, `rating`, `status` |
| `article` | Article notes | `source`, `author` |
| `idea` | Captured idea | `status` |
| `log` | Changelog/work log | `project` |
| `template` | Reusable template | — |

## Content Formatting

### Headings and Structure

Use a clear heading hierarchy. The note title comes from the filename — start content with an H2 (`##`) or go straight into prose. Never start with an H1 that duplicates the filename.

```markdown
## Overview

Brief description of the topic.

## Key Points

- First important thing
- Second important thing

## Details

### Subtopic A

Content here...

### Subtopic B

Content here...

## References

- [[Related Note]]
- [External Resource](https://example.com)
```

### Internal Links

Use wikilinks liberally — they're the backbone of a connected vault:

- `[[Note Name]]` — basic link
- `[[Note Name|Display Text]]` — aliased link
- `[[Note Name#Heading]]` — link to a specific section
- `![[Note Name]]` — embed another note

When creating notes that reference concepts, people, or projects — link to them even if the target note doesn't exist yet. Obsidian highlights unresolved links, which helps the user see what notes to create next.

### Callouts

Use callouts to highlight important information:

```markdown
> [!tip] Pro Tip
> This is especially useful when...

> [!warning] Watch Out
> Be careful about...

> [!info] Context
> Background information...

> [!example] Example
> Here's how this works in practice...

> [!question] Open Question
> Something to think about...

> [!summary] TL;DR
> The key takeaway is...
```

Use callouts sparingly — one or two per note is usually right. They lose impact when overused.

### Lists and Tasks

```markdown
- Regular bullet point
  - Nested item
- [ ] Unchecked task
- [x] Completed task
```

### Tables

Use markdown tables for structured data:

```markdown
| Column A | Column B | Column C |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
```

### Code Blocks

Use fenced code blocks with language identifiers:

````markdown
```python
def hello():
    print("Hello, world!")
```
````

## Folder Conventions

When placing notes, follow these common patterns (adapt to what already exists in the vault):

```
/                       # Vault root
├── 00 - Inbox/         # Quick captures, unsorted notes
├── 01 - Projects/      # Active project folders
├── 02 - Areas/         # Ongoing areas of responsibility
├── 03 - Resources/     # Reference material, learning notes
├── 04 - Archives/      # Completed/inactive content
├── Daily/              # Daily notes
├── Templates/          # Note templates
└── Attachments/        # Images, PDFs, etc.
```

However — if the user's vault already has a different structure, match it. Don't impose PARA or any other system on an existing vault. If the vault is empty, suggest a simple starting structure but let the user decide.

## Multi-Note Creation

When the user asks for something that naturally involves multiple notes (a project setup, a knowledge base on a topic, a vault structure), create them all. For instance, "set up a project for X" might produce:

1. A **project MOC** note that links to everything
2. A **goals/objectives** note
3. A **meeting notes** folder with a template
4. Any initial content notes

Connect them all with internal links so the user has a navigable structure from the start.

## Quality Checklist

Before finishing, verify each note has:

- [ ] Meaningful frontmatter (not boilerplate)
- [ ] Clean heading hierarchy (no H1 duplicating filename)
- [ ] Internal links to related concepts
- [ ] Appropriate use of callouts (not overdone)
- [ ] Tags that follow a consistent hierarchy
- [ ] Proper placement in the vault folder structure
- [ ] Content that reads well as standalone prose (not just bullet dumps)
