# dave-plugins

## Overview
Dave's personal Claude Code plugin collection. A marketplace package bundling multiple plugins that add skills for development workflows, cloud infrastructure management, and proposal generation. Installed globally across all Claude Code sessions.

## Venture
Personal

## Classification
Independent - Dave Braendler owned

## Status
Active

## Users
Dave Braendler — used across all Claude Code sessions via marketplace install.

## Commercial Value
Productivity multiplier across all dev work. Codifies repeatable workflows (spec writing, code scanning, GCP deploys, cost analysis, proposal generation) into reusable Claude Code skills.

## Dependencies
- Claude Code (plugin host)
- Google Cloud SDK (gcloud-tools plugin)
- Node.js + docx package (proposal plugin)

## Current State
Three plugins shipping with five skills total. Two legacy tools parked in `to-migrate/` awaiting rethinking (website-to-markdown crawler and PDF scanner).

---

# Feature Register

> Living register of shipped capabilities. Updated as features land.
> Last updated: 2026-03-21

## Development Skills (`dev`)
| Feature | Status | Description |
|---------|--------|-------------|
| `/dev:spec-writer` | Shipped | Generate structured specs with architecture, data models, API, and agent tasks |
| `/dev:code-scanner` | Shipped | Scan codebase to extract classes, methods, imports, and code smells |

## GCP Tools (`gcloud-tools`)
| Feature | Status | Description |
|---------|--------|-------------|
| `/gcloud-tools:gcloud-deploy` | Shipped | Package projects for Cloud Run with Dockerfile, cloudbuild.yaml, and custom domains |
| `/gcloud-tools:gcloud-costs` | Shipped | Check GCP billing, costs by service/project, budgets, and cleanup recommendations |

## Proposal Generator (`proposal`)
| Feature | Status | Description |
|---------|--------|-------------|
| `/proposal:generic` | Shipped | Generate Blue Harbour .docx proposals across five service lines |

## Spec Writer Details
| Feature | Status | Description |
|---------|--------|-------------|
| Structured output | Shipped | 8-section spec: overview, architecture, data models, API, frontend, JSON schemas, agent tasks, acceptance criteria |
| Agent task breakdown | Shipped | Parallel workstreams with dependency tracking for Claude Code execution |
| Scope inference | Shipped | Extracts stack, scope, and context from brief user input |

## Code Scanner Details
| Feature | Status | Description |
|---------|--------|-------------|
| Python analysis | Shipped | Packages, classes, methods, async functions, line counts |
| JS/TS analysis | Shipped | Imports, classes, functions, exports, ES6 and CommonJS |
| Code smell detection | Shipped | Duplicate names, large files (>200 lines), large classes (>=10 methods) |
| Import alias analysis | Shipped | Suggests path alias fixes and consolidated imports for JS/TS |
| Report generation | Shipped | Outputs `project_structure_report.md` with summary stats |

## GCloud Deploy Details
| Feature | Status | Description |
|---------|--------|-------------|
| Static SPA deployment | Shipped | Multi-stage Docker build with nginx for Vite/React/Next.js |
| Node.js server deployment | Shipped | Single-stage Docker build for Express/Fastify/Hono |
| Package manager detection | Shipped | Auto-detects npm, bun, pnpm, yarn from lock files |
| Env var separation | Shipped | Distinguishes build-time (VITE_*) vs runtime env vars |
| Custom domain setup | Shipped | Global HTTPS Load Balancer with managed SSL certificates |
| IAM permissions guide | Shipped | Full service account setup for Cloud Build pipeline |
| Troubleshooting table | Shipped | 11 common deployment errors with causes and fixes |

## GCloud Costs Details
| Feature | Status | Description |
|---------|--------|-------------|
| Billing overview | Shipped | Lists accounts, linked projects, and budgets |
| Cost breakdown | Shipped | Per-service/project costs via BigQuery export or CLI |
| Cloud Run metrics | Shipped | Service usage, revisions, and resource allocation |
| Cost optimization | Shipped | Actionable cleanup recommendations for idle resources |
| Resource cleanup | Shipped | Delete unused services, old images, and disabled APIs |

## Proposal Generator Details
| Feature | Status | Description |
|---------|--------|-------------|
| Five service lines | Shipped | capital_planning, ai_agents, reporting, data_enablement, generic |
| Auto-fill defaults | Shipped | Service line templates provide context, pain points, objectives, deliverables |
| Unstructured input parsing | Shipped | Extracts params from emails or brief descriptions |
| Auto-incrementing refs | Shipped | Proposal reference numbers auto-increment from last generated |
| .docx output | Shipped | Professional branded document with Blue Harbour formatting |

## Legacy / Parked
| Feature | Status | Description |
|---------|--------|-------------|
| Website-to-markdown crawler | Parked | Multi-page website crawler with chunking, needs lighter reimagining |
| PDF scanner | Parked | PDF text + image extraction with OCR, needs reimagining without local ML stack |

## Recent Changes
| Date | Change |
|------|--------|
| 2026-03-21 | Migrated codescanner to `/dev:code-scanner` skill, killed RAG tool, added to-migrate notes |
| 2026-03-21 | Added proposal generator plugin with five service lines |
| 2026-03-21 | Added gcloud-tools plugin with deploy and costs skills |
| 2026-03-21 | Initial repo structure with dev plugin and spec-writer skill |

---
*Structured for GitHub-Powered IP Register sync. Fields above are read by the dashboard.*
