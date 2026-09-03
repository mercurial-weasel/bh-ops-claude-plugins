---
name: obsidian-markdown-guide
description: Generate well-formed Obsidian-compatible markdown files with structured YAML frontmatter, wikilinks, callouts, and proper heading hierarchy. Use this skill whenever creating or editing .md files destined for an Obsidian vault — including notes, meeting records, decision records, person profiles, or any structured knowledge capture. Also trigger when the user mentions "vault", "Obsidian note", "frontmatter", "YAML properties", or asks to create notes with metadata, tags, or linked references.
---

# Obsidian Markdown File Generation

This skill defines how to produce well-formed Obsidian-compatible markdown files. Follow these rules when generating any `.md` file intended for an Obsidian vault.

## Quick Reference

1. Every file starts with a `---` YAML frontmatter block
2. Required fields: `title`, `type`, `status`, `tags`, `created`, `updated`
3. Body starts at H2 — never use H1 (Obsidian uses filename/title as H1)
4. Internal links use `[[wikilinks]]`, external links use `[text](url)`
5. Tags are lowercase, hyphenated, no `#` prefix in frontmatter
6. Dates are `YYYY-MM-DD`, unquoted

## Frontmatter Template

```yaml
---
title: "Note Title"
type: note
status: active
tags:
  - topic-one
  - topic-two
created: 2026-03-21
updated: 2026-03-21
---
```

For the full specification — including all field types, note type archetypes, special templates (meetings, decisions, people), anti-patterns, and Dataview compatibility — read `references/guide.md`.

## Note Types

| Type | Use Case |
|------|----------|
| `note` | General knowledge capture |
| `reference` | External material, specs |
| `meeting` | Meeting notes with attendees, decisions, actions |
| `decision` | Decision record (context, options, outcome) |
| `project` | Project overview / index |
| `person` | Contact or stakeholder profile |
| `log` | Daily log, journal |
| `moc` | Map of Content — index linking related notes |
| `action` | A discrete task or open loop |
| `framework` | Reusable model or methodology |
| `artefact` | Produced deliverable |

## Key Rules

- **File naming:** kebab-case, no spaces: `capital-planning-framework.md`
- **Tags:** YAML list format, never comma-separated. No `#` prefix.
- **Dates:** ISO 8601 unquoted so Dataview can parse them.
- **Strings with colons:** Must be quoted in YAML.
- **Empty fields:** Omit entirely or use `null` — never leave blank.
- **Heading hierarchy:** Strict — never skip levels (H2 → H4 is wrong).
- **Callouts:** Use `> [!type]` syntax for warnings, tips, notes, etc.
- **Linking:** `[[wikilinks]]` for vault notes, `[text](url)` for external only.

## Before Saving Checklist

- Frontmatter block present and valid YAML
- Required fields populated (`title`, `type`, `status`, `tags`, `created`, `updated`)
- Tags lowercase, hyphenated, no `#`
- Dates `YYYY-MM-DD`, unquoted
- Body starts at H2
- Internal links use `[[wikilinks]]`
- No empty frontmatter fields, no tabs in YAML
