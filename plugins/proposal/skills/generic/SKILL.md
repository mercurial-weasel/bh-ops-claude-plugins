---
name: generic
description: Generate a Blue Harbour workshop proposal as a professional .docx document. Use when Dave asks to create a proposal, draft a proposal, or when processing an inbound email/request that needs a proposal generated.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
---

# Blue Harbour Workshop Proposal Generator

You are generating a Blue Harbour workshop proposal. The proposal generator lives at `plugins/proposal/proposal-generator/` relative to the dave-plugins repo root.

## Usage

```
/proposal:generic
/proposal:generic Capital planning workshop for Metro Transit Authority, contact Jordan Ellis PMO Head
```

**When to use:** When you need to generate a workshop proposal. Can parse structured input, a brief description, or even a raw email.

**Service lines available:**
- `capital_planning` — Capital Planning & Portfolio Intelligence
- `ai_agents` — Intelligent Agent Services
- `reporting` — Intelligent Reporting Platform
- `data_enablement` — Data Enablement
- `generic` — Custom / Advisory Services

**What you'll need to provide (minimum):**
- Client name, contact name, and contact title
- Service line

**What's auto-filled if omitted:**
- Workshop title, context, pain points, objectives, deliverables (from service line defaults)
- Proposal date (today), expiry (today + 30 days), ref number (auto-incremented)
- Blue Harbour team details, branding, contact info

**What you get back:** A professional `.docx` proposal in `plugins/proposal/proposal-generator/output/`.

**Examples:**
```
/proposal:generic client: Northwind Utilities, contact: Alex Stanton, title: Head of Capital Planning, service: capital_planning
/proposal:generic <paste an email from a prospect>
/proposal:generic
```

## Step 1 — Gather parameters

Extract or ask for the following required fields:
- **client_name** — the client organisation name
- **client_contact** — the primary contact's name
- **client_title** — the contact's job title
- **service_line** — one of: `capital_planning`, `ai_agents`, `reporting`, `data_enablement`, `generic`
- **workshop_title** — full title (or leave blank to use service line default)

Optional but useful:
- `client_email`, `proposed_date`, `follow_on_indicative`, `context`, `pain_points`, `objectives`

If the user provides unstructured input (e.g. an email), extract these fields intelligently. Use the service line to fill in defaults for content fields that aren't provided.

## Step 2 — Build the params JSON

Construct a JSON object with only the fields the user provided or that you extracted. Do NOT include fields that should use defaults — the generator handles merging.

## Step 3 — Ensure dependencies are installed

Before first run, check that `node_modules` exists in the proposal-generator directory:

```bash
cd <repo-root>/plugins/proposal/proposal-generator && [ -d node_modules ] || npm install
```

## Step 4 — Generate the proposal

Run the generator with the params:

```bash
cd <repo-root>/plugins/proposal/proposal-generator && node generate.js --json '<params_json>'
```

The generator will:
- Merge service line defaults for any omitted fields
- Auto-generate `proposal_ref` (incrementing from last generated)
- Set `proposal_date` to today and `proposal_expiry` to today + 30 days
- Output the .docx file to `plugins/proposal/proposal-generator/output/`

## Step 5 — Report back

Tell the user:
- The file path of the generated proposal
- The proposal reference number
- Client name and service line
- Offer to open or review the content

## Notes

- The generator is a Node.js script using the `docx` package
- All Blue Harbour branding defaults (lead, email, phone, web) are built in
- Service line defaults provide context, pain points, objectives, and deliverables — only override these if the user provides specific content
- The params schema is in `params-schema.json` for reference
- Example params are in `example-params/` for reference
