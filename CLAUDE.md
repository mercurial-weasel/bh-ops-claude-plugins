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

## Known context

- **GCP billing account:** `01215E-8780EA-F709E1` (My Billing Account)
- **Primary GCP project:** `blue-harbour-marketing`
- **GCP region:** `australia-southeast1`
