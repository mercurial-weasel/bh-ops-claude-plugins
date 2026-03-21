---
name: code-scanner
description: >
  Scan a codebase and produce a structured project overview report. Extracts packages, classes, methods,
  standalone functions, imports, line counts, inheritance, and code smells. Works with Python, JavaScript,
  and TypeScript projects. Use when the user asks to "scan this project", "give me an overview",
  "what's in this codebase", "map the code structure", "analyze this repo", or any request to understand
  a project's structure before refactoring, onboarding, or code review.
---

# Code Scanner

Produces a structured markdown report of a codebase's architecture — packages, classes, methods, functions, imports, and code smells.

## Usage

```
/dev:code-scanner
/dev:code-scanner scan ./src
/dev:code-scanner scan this project with imports
```

## Inputs

1. **Target path** — which directory to scan (default: current working directory)
2. **Options** (ask only if not specified):
   - Include imports? (default: no for Python, yes for JS/TS)
   - Include private/underscore members? (default: no)
   - Include docstrings? (default: no)
   - Generate import alias suggestions? (JS/TS only, default: no)

---

## Procedure

### Step 1: Detect project type

Use Glob to check for project markers:

- `**/*.py` + `__init__.py` files → Python project
- `package.json` or `**/*.ts` / `**/*.tsx` / `**/*.js` / `**/*.jsx` → Node.js/TypeScript project
- Mixed → scan both

Read `package.json`, `pyproject.toml`, or `setup.py` if present for project metadata.

### Step 2: Discover files

Use Glob to find all source files. Exclude:
- `node_modules/`, `venv/`, `.venv/`, `env/`, `__pycache__/`, `dist/`, `build/`, `.git/`
- Test fixtures, generated files, lock files

Count total files by extension.

### Step 3: Analyze each file

Read each source file and extract:

**For Python files:**
- Package detection (`__init__.py` presence)
- Classes: name, base classes, method count, method names with line counts
- Standalone functions: name, line count
- Async functions/methods (mark with `async` prefix)
- Total line count per file
- Docstrings (if option enabled)
- Import statements (if option enabled)

**For JS/TS files:**
- Import statements (ES6 `import` and CommonJS `require`)
- Class definitions and names
- Function declarations (named `function` keyword)
- Export patterns

**For both:**
- Flag files over 200 lines
- Flag classes with 10+ methods

### Step 4: Detect code smells

Scan the collected data for:
- **Duplicate function names** across files (especially `main`, `run`, `process`, `initialize`, `start`, `parse_arguments`)
- **Large files** (>200 lines)
- **Large classes** (>=10 methods)
- **Deep relative imports** in JS/TS (multiple `../` levels)

### Step 5: Path alias analysis (JS/TS only, if requested)

Read config files for path aliases:
- `vite.config.ts` — look for `resolve.alias` entries
- `tsconfig.json` — look for `compilerOptions.paths`
- `vitest.config.ts` — same as vite

Then identify imports that use relative paths (`../../`) which could use aliases instead. Suggest:
- Individual import fixes (relative → alias)
- Consolidated imports (multiple imports from same source → single import)
- New alias suggestions for commonly traversed paths

### Step 6: Generate the report

Write the report to a markdown file in the project root (default: `project_structure_report.md`).

---

## Report Format

Use this exact structure:

```markdown
# Project Structure Report

- **Scan performed:** {timestamp}
- **Target location:** `{path}`
- **Project type:** {Python | Node.js/TypeScript | Mixed}

---

## Config Files

{If JS/TS: include contents of vite.config.ts, vitest.config.ts if they exist}

---

## Guidelines

{Include the appropriate guidelines section below based on project type}

---

## Packages

- {package path}
- {package path}

---

## Potential Code Duplication

{Only if duplicates found}
- `{function_name}` found in {N} files: {file1}, {file2}

---

## Classes, Files and Functions by Folder

### {folder_path}

#### **{filename}** _{line_count} lines{" (large file)" if >200}_

**{ClassName}** ({BaseClass1, BaseClass2}) - {method_count} methods {" (large class)" if >=10}
  - `{method_name} ({line_count} lines)`
  - `async {method_name} ({line_count} lines)`

**Standalone Functions**
  - `{function_name} ({line_count} lines)`

**Imports** {if enabled}
  - `import x from 'y'`
  - `from module import name`

---

## Project Summary

- **Total Files**: {N}
- **Total Classes**: {N}
- **Total Methods**: {N}
- **Total Standalone Functions**: {N}
- **Total Lines of Code**: {N}
- **Packages**: {N}
- **Files > 200 Lines**: {N}
- **Classes with >= 10 Methods**: {N}
- **Common Functions Duplicated Across Files**: {N}
- **Average Lines per File**: {N}
- **Average Methods per Class**: {N}
```

---

## Guidelines to Include in Report

### For Python projects:

> This report documents the structure of a Python project — packages, classes, files, and functions.
> It supports refactoring, code review, architecture review, and onboarding.
>
> **What a reviewer should consider:**
> - Whether files could be combined or split
> - Classes with too many methods (SRP violation)
> - Files or folders that could become modules or sub-packages
> - Duplicate or similar function names across files
> - Helper functions that should be moved to utilities
> - Functions that should be grouped into cohesive classes
> - Opportunities to replace inheritance with composition

### For JS/TS projects:

> This report documents the structure of a Node.js/TypeScript project — modules, classes, files, functions, and imports.
> It supports refactoring, code review, architecture review, onboarding, and import optimization.
>
> **What a reviewer should consider:**
> - Whether the project follows Node.js best practices
> - Classes with too many methods (SRP violation)
> - Files that could be split into smaller, focused modules
> - Duplicate or similar function names across files
> - Separation between routes, controllers, models, and services
> - Import patterns — use path aliases instead of deep relative paths
> - Consolidate multiple imports from the same source
> - Tightly coupled modules visible in the import graph

---

## Import Fixes Report (JS/TS, separate file if requested)

If import alias analysis is requested, write a second file `suggested_import_changes.md`:

```markdown
# Suggested Import Changes

## Path Aliases Available
- `@alias` -> `path`

## Suggested Import Changes by File

### {relative_file_path}

#### Individual Import Changes

Line {N}:
```typescript
// Original:
import { X } from '../../components/common'

// Suggested:
import { X } from '@common'
```

#### Consolidated Import Suggestions
```typescript
// Original separate imports:
import { Header } from '@common'
import { Footer } from '@common'

// Consolidated import:
import { Header, Footer } from '@common'
```

## Suggested New Aliases
{If commonly traversed paths don't have aliases yet}
```

---

## Performance Notes

- For large projects (100+ files), use the Agent tool with subagents to scan folders in parallel
- Read files in batches — don't try to read every file sequentially
- Skip binary files, images, and generated code
- For the summary stats, count as you go rather than re-scanning
