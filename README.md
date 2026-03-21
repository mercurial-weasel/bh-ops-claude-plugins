# dave-plugins

## Overview
Dave's personal Claude Code plugin collection. A marketplace package bundling multiple plugins that add skills for development workflows, cloud infrastructure management, and proposal generation.

## Venture
Personal

## Classification
Independent - Dave Braendler owned

## Status
Active

## Users
Dave Braendler — used across all Claude Code sessions via marketplace install.

## Commercial Value
Productivity multiplier across all dev work. Codifies repeatable workflows (spec writing, code scanning, GCP deploys, proposal generation) into reusable Claude Code skills.

## Dependencies
- Claude Code (plugin host)
- Google Cloud SDK (gcloud-tools plugin)
- Node.js + python-docx (proposal plugin)

## Current State
Three plugins shipping with five skills total. Two legacy tools parked in `to-migrate/` awaiting rethinking.

---

# Feature Register

> Living register of shipped capabilities. Updated as features land.
> Last updated: 2026-03-21

## Development Skills (`dev`)
| Feature | Status | Description |
|---------|--------|-------------|
| `/dev:spec-writer` | Shipped | Generate structured technical specs for agentic execution |
| `/dev:code-scanner` | Shipped | Scan a codebase and produce a structured project overview report |

## GCP Tools (`gcloud-tools`)
| Feature | Status | Description |
|---------|--------|-------------|
| `/gcloud-tools:gcloud-deploy` | Shipped | Package projects for Cloud Run deployment via Cloud Build |
| `/gcloud-tools:gcloud-costs` | Shipped | Check GCP billing, costs, budgets, and spending breakdowns |

## Proposal Generator (`proposal`)
| Feature | Status | Description |
|---------|--------|-------------|
| `/proposal:generic` | Shipped | Generate Blue Harbour workshop proposals as .docx documents |

## Recent Changes
| Date | Change |
|------|--------|
| 2026-03-21 | Migrated codescanner to `/dev:code-scanner` skill, killed RAG tool, added to-migrate notes |
| 2026-03-21 | Added proposal generator plugin |
| 2026-03-21 | Added gcloud-tools plugin with deploy and costs skills |
| 2026-03-21 | Initial repo structure with dev plugin and spec-writer skill |

---
*Structured for GitHub-Powered IP Register sync. Fields above are read by the dashboard.*
