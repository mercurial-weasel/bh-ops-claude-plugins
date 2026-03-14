# Available Skills

This plugin package provides the following skills for Claude Code.

## dev plugin

### /dev:spec-writer
Generate a comprehensive technical specification document optimised for Claude Code agentic execution. Use when speccing out a feature, system, or product.

**Triggers:** "write a spec", "create a spec", "spec this out", "I want to build X", "create a technical plan"

**Output:** A single structured markdown document covering architecture, data models, API, frontend components, parallel agent task breakdown, and acceptance criteria.

---

## gcloud-tools plugin

### /gcloud-tools:gcloud-costs
Check Google Cloud billing setup, current costs, cost breakdowns by service/project, and budget alerts.

**Triggers:** "how much am I spending on GCP", "check my cloud costs", "what's my billing", "GCP budget"

**What it does:**
- Lists billing accounts and linked projects
- Queries cost breakdowns by service and project (via BigQuery export if available)
- Shows Cloud Run service usage and resource allocation
- Lists enabled APIs, Artifact Registry storage, and Cloud Build history
- Provides cost optimization recommendations
- Can clean up unused resources (with confirmation)

**Tools used:** Bash only (no model invocation — runs gcloud commands directly)

---

### /gcloud-tools:gcloud-deploy
Package and prepare a project for deployment to Google Cloud Run via Cloud Build.

**Triggers:** "deploy to cloud run", "set up GCP deployment", "create a Dockerfile for cloud run", "package for deployment"

**What it does:**
- Analyzes the project (package manager, framework, build output, env vars)
- Determines deployment strategy (static SPA via nginx or Node.js server)
- Generates/updates `Dockerfile`, `cloudbuild.yaml`, `nginx.conf.template`, `.dockerignore`
- Guides full GCP project setup: billing, IAM permissions, Artifact Registry
- Sets up custom domains via Global HTTPS Load Balancer (with SSL)
- Includes troubleshooting table for common deployment errors

**Supported stacks:**
- Static SPAs: Vite, React, Next.js static export
- Node.js servers: Express, Fastify, Hono
- Package managers: npm, bun, pnpm, yarn

**Tools used:** Read, Glob, Grep, Bash, Edit, Write
