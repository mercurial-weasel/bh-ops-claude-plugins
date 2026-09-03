# dave-plugins

Dave's personal Claude Code plugin collection. This marketplace package bundles multiple plugins that add skills for development workflows and cloud infrastructure management.

## Structure

```
dave-plugins/
├── .claude-plugin/marketplace.json   # Plugin registry
├── plugins/
│   ├── dev/                          # Development skills
│   │   └── skills/
│   │       └── spec-writer/          # /dev:spec-writer
│   └── gcloud-tools/                 # GCP skills
│       └── skills/
│           ├── gcloud-costs/         # /gcloud-tools:gcloud-costs
│           └── gcloud-deploy/        # /gcloud-tools:gcloud-deploy
```

## Plugins

### dev
Development productivity skills — spec generation, project scaffolding.

### gcloud-tools
Google Cloud Platform tools — Cloud Run deployment packaging, billing/cost analysis, budget monitoring.

## Adding a new skill

1. Create `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`
2. If it's a new plugin, create `plugins/<plugin-name>/.claude-plugin/plugin.json` and register it in `.claude-plugin/marketplace.json`
3. Skill frontmatter requires: `name`, `description`, and optionally `allowed-tools`, `disable-model-invocation`

## Context

This repo is a public plugin marketplace. **It must carry no real identifiers** — no GCP
project ids or numbers, no billing account ids, no client or contact names, no email
addresses, and no fee figures. Skills resolve those at runtime from the repository they are
invoked in (see `gcloud-costs` step 0) or take them as arguments.

An earlier version of this file pinned one organisation's billing account, project and region
here. That is the class of thing that leaks from a public repo without anyone thinking of it
as content.
