---
name: gcloud-costs
description: Check Google Cloud billing setup, current costs, cost breakdowns by service/project, and budget alerts. Use when the user asks about GCP spending, billing, costs, budgets, or wants to understand what they're being charged for.
disable-model-invocation: true
allowed-tools: Bash
---

# Google Cloud Costs & Billing

You are helping the user understand their Google Cloud billing and costs.

## Usage

```
/gcloud-tools:gcloud-costs
/gcloud-tools:gcloud-costs cloud run costs
/gcloud-tools:gcloud-costs this month
/gcloud-tools:gcloud-costs <project-id>
```

**When to use:** When you want to check GCP spending, billing, costs, budgets, or understand what you're being charged for.

**What you can ask:**
- Current month's costs (overall or by service/project)
- Cloud Run, Artifact Registry, or Cloud Build usage
- Budget status and alerts
- Cost optimisation recommendations
- Clean up unused resources

**What you get back:** A formatted cost summary table with recommendations for savings.

**Billing account:** discovered at run time — see §0. The skill holds no account, project or region of its own.

## Arguments

`$ARGUMENTS` — Optional: a project ID, date range, or specific query (e.g. "this month", "cloud run costs", "all projects").

## What to do

Run the relevant gcloud commands below based on what the user asks. Present results in a clear, readable format with totals and highlights.

### 1. Billing account overview

```bash
# List billing accounts
gcloud billing accounts list

# Show which projects are linked to billing
gcloud billing projects list --billing-account=BILLING_ACCOUNT_ID
```

### 2. Current costs via BigQuery billing export

If BigQuery billing export is enabled:
```bash
# Query costs for current month
bq query --use_legacy_sql=false "
SELECT
  project.id AS project,
  service.description AS service,
  ROUND(SUM(cost), 2) AS cost,
  currency
FROM \`PROJECT_ID.billing_dataset.gcp_billing_export_v1_BILLING_ACCOUNT_ID\`
WHERE invoice.month = FORMAT_DATE('%Y%m', CURRENT_DATE())
GROUP BY project, service, currency
ORDER BY cost DESC
"
```

### 3. Cost estimates via Cloud Run metrics

For Cloud Run specifically (most common for this user):
```bash
# List all Cloud Run services across projects
gcloud run services list --format="table(metadata.name, status.url, metadata.labels.'cloud.googleapis.com/location')"

# Get usage metrics for a specific service
gcloud run services describe SERVICE_NAME --region=REGION --format="yaml(status.traffic, spec.template.spec.containers[0].resources)"

# Check number of revisions (each consumes resources)
gcloud run revisions list --service=SERVICE_NAME --region=REGION --format="table(metadata.name, status.conditions[0].status, metadata.creationTimestamp)"
```

### 4. Cost breakdown using billing CLI

```bash
# Get cost breakdown for current billing period
gcloud billing budgets list --billing-account=BILLING_ACCOUNT_ID

# Describe a specific budget
gcloud billing budgets describe BUDGET_ID --billing-account=BILLING_ACCOUNT_ID
```

### 5. Quick cost check via gcloud

```bash
# List all enabled APIs (each may incur costs)
gcloud services list --enabled --project=PROJECT_ID

# Check Artifact Registry storage (images consume storage)
gcloud artifacts docker images list REGION-docker.pkg.dev/PROJECT_ID/REPO_NAME --format="table(package, createTime, updateTime)" --sort-by=~createTime --limit=10

# Check Cloud Build history (builds consume compute)
gcloud builds list --limit=10 --format="table(id, status, createTime, duration, source.storageSource.bucket)"
```

### 6. Cost optimization tips

After gathering data, provide actionable advice:

- **Idle Cloud Run services** with 0 req/sec — suggest deleting or scaling to 0 min instances
- **Old container images** in Artifact Registry — suggest cleanup to reduce storage costs
- **Multiple projects** with similar services — suggest consolidation
- **Unused APIs** — suggest disabling to avoid accidental charges
- **Cloud Build frequency** — if building often, consider caching layers

### 7. Clean up unused resources

```bash
# Delete a Cloud Run service
gcloud run services delete SERVICE_NAME --region=REGION --project=PROJECT_ID

# Delete old images (keep latest N)
gcloud artifacts docker images list REGION-docker.pkg.dev/PROJECT_ID/REPO_NAME --format="value(package)" --sort-by=createTime | head -n -3 | xargs -I{} gcloud artifacts docker images delete {} --quiet

# Disable unused APIs
gcloud services disable API_NAME --project=PROJECT_ID
```

## Presentation format

Always present costs in a clear table format:

```
## GCP Cost Summary

**Billing Account:** Example Billing Account (XXXXXX-XXXXXX-XXXXXX)
**Period:** March 2026

| Project | Service | Cost (USD) |
|---------|---------|-----------|
| example-project | Cloud Run | $0.00 |
| example-project | Artifact Registry | $0.12 |
| example-project | Cloud Build | $0.05 |
| **Total** | | **$0.17** |

### Recommendations:
- Service X has 0 requests — consider deleting to avoid minimum charges
- 15 old container images found — clean up to save storage costs
```

## 0. Establish context before running anything

Do not assume a project, a billing account or a region. Resolve them in this order, and stop
to confirm with the user if a step is ambiguous.

**Project** — check the repo's `CLAUDE.md` for a `## Deployment` or `## GCP` section first. If
it names a project, region or service, **use those values**; they are the project this codebase
belongs to. Only if there is no such section, fall back to the machine default and confirm it:

```bash
gcloud config get-value project
```

**Critical:** always pass `--project <project-id>` explicitly. The machine default may not be
the project for this codebase, and cost commands read whichever project they are given without
complaint.

**Billing account** — discover it rather than assuming:

```bash
gcloud billing projects describe PROJECT_ID --format='value(billingAccountName)'
gcloud billing accounts list                      # if the above is empty
gcloud billing projects list --billing-account=BILLING_ACCOUNT_ID   # sibling projects
```

**Region** — read it from the deployed services rather than guessing:

```bash
gcloud run services list --project PROJECT_ID --format='value(metadata.name,metadata.labels."cloud.googleapis.com/location")'
```

> [!note] Why this skill holds no identifiers
> An earlier version hardcoded one organisation's project, project number, billing account and
> region under a "Known user context" heading. Those are not secrets — a project ID grants
> nothing, IAM does — so they do not belong in a secret store either. They are *context*, and
> context belongs to the repository the skill is invoked in, not to the skill. Discovering them
> makes the skill work for any project instead of silently reporting on the wrong one.

## Important rules

- Always show costs in the user's currency
- Highlight any services with $0 usage that could be deleted
- Flag any unexpected or high costs
- Keep commands on single lines (no backslash line continuations)
- If BigQuery billing export isn't set up, suggest enabling it for detailed cost tracking
- Cloud Run free tier: 2 million requests/month, 360,000 GB-seconds, 180,000 vCPU-seconds — mention when relevant
