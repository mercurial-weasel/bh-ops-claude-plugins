---
name: gcloud-costs
description: Check Google Cloud billing setup, current costs, cost breakdowns by service/project, and budget alerts. Use when the user asks about GCP spending, billing, costs, budgets, or wants to understand what they're being charged for.
disable-model-invocation: true
allowed-tools: Bash
---

# Google Cloud Costs & Billing

You are helping the user understand their Google Cloud billing and costs.

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

**Billing Account:** My Billing Account (01215E-8780EA-F709E1)
**Period:** March 2026

| Project | Service | Cost (USD) |
|---------|---------|-----------|
| blue-harbour-marketing | Cloud Run | $0.00 |
| blue-harbour-marketing | Artifact Registry | $0.12 |
| blue-harbour-marketing | Cloud Build | $0.05 |
| **Total** | | **$0.17** |

### Recommendations:
- Service X has 0 requests — consider deleting to avoid minimum charges
- 15 old container images found — clean up to save storage costs
```

## Known user context

- **Primary billing account:** `01215E-8780EA-F709E1` (My Billing Account)
- **Primary project:** `blue-harbour-marketing` (project number: `72678620841`)
- **Region:** `australia-southeast1`
- **Other projects on same billing:** Check with `gcloud billing projects list`
- **gcloud CLI:** Available locally

## Important rules

- Always show costs in the user's currency
- Highlight any services with $0 usage that could be deleted
- Flag any unexpected or high costs
- Keep commands on single lines (no backslash line continuations)
- If BigQuery billing export isn't set up, suggest enabling it for detailed cost tracking
- Cloud Run free tier: 2 million requests/month, 360,000 GB-seconds, 180,000 vCPU-seconds — mention when relevant
