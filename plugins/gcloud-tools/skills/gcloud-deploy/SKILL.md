---
name: gcloud-deploy
description: Package and prepare a project for deployment to Google Cloud Run. Generates or updates Dockerfile, cloudbuild.yaml, and nginx.conf.template files for deploying static frontend apps (Vite/React/Next.js static export) or Node.js backends to Cloud Run via Cloud Build. Also covers full GCP project setup, IAM permissions, billing, custom domain mapping, and troubleshooting.
allowed-tools: Read, Glob, Grep, Bash, Edit, Write
---

# Google Cloud Run Deployment Packager

You are helping the user package their project for deployment to **Google Cloud Run** via **Cloud Build**.

## Usage

```
/gcloud-tools:gcloud-deploy
/gcloud-tools:gcloud-deploy my-service-name
/gcloud-tools:gcloud-deploy dry-run
```

**When to use:** When you want to deploy a project to Cloud Run. Handles Dockerfile, cloudbuild.yaml, nginx config, IAM permissions, custom domains, and troubleshooting.

**Supported project types:**
- Static SPAs (Vite, React, Next.js static export) — builds with nginx
- Node.js servers (Express, Fastify, Hono) — builds with node runtime

**What you'll need to provide:**
- GCP project ID (or create a new one)
- Service name (defaults to package.json name)
- Region preferences for registry and deployment

**What you get back:** Generated deployment files (Dockerfile, cloudbuild.yaml, nginx.conf.template, .dockerignore) plus a step-by-step deployment guide.

## Arguments

`$ARGUMENTS` — Optional flags or context, e.g. a service name, region, or "dry-run" to only preview files.

## Step-by-step process

### 0. Check for project-specific deployment config

Before anything else, check `CLAUDE.md` for a `## Deployment` section. If it exists, it will have the GCP project, region, and service name already configured. **Use these values** — do not ask the user or rely on the default gcloud project.

If no deployment config is found in CLAUDE.md, check the current gcloud project with `gcloud config get-value project` and confirm with the user that it's correct before proceeding.

**Critical:** Always include `--project <project-id>` in all gcloud commands. The user's default gcloud project may not match the project for this codebase.

### 1. Analyze the project

- Read `package.json` (or equivalent) to determine:
  - Build command (e.g. `npm run build`, `bun build`)
  - Package manager — check for `bun.lockb` (bun), `pnpm-lock.yaml` (pnpm), `yarn.lock` (yarn), or `package-lock.json` (npm)
  - Output directory — check `vite.config.*` for `build.outDir` (default `dist`), or `next.config.*` for `distDir`
  - Whether it's a static SPA or a Node.js server (look for `express`, `fastify`, `@hono/node-server` in dependencies, or a `start` script that runs a server)
  - Runtime dependencies
- Check for existing deployment files: `Dockerfile`, `cloudbuild.yaml`, `nginx.conf.template`, `.dockerignore`
- Scan source files for env var usage to identify build-time variables:
  - Vite: `import.meta.env.VITE_*` — grep for `VITE_` in `src/`
  - Next.js: `process.env.NEXT_PUBLIC_*` — grep for `NEXT_PUBLIC_` in `src/` and `app/`
  - Also check `.env`, `.env.example`, `.env.local` files for the canonical list of variable names
- **Check if env vars are actually client-side or server-side only.** If a key like `GEMINI_API_KEY` is only used in server-side code (e.g. Convex actions, Express routes), do NOT include it as a build-time arg. Only include env vars that are actually embedded in the client bundle (e.g. `VITE_*` vars referenced via `import.meta.env`).
- Check `vite.config.*` for any `define` blocks that inject env vars — if they reference server-side-only keys, flag this as a cleanup opportunity.
- Check for a `vite.config.*` or `next.config.*` to confirm the framework

### 2. Determine deployment strategy

**Static SPA** (Vite, CRA, static Next.js export):
- Multi-stage Dockerfile: `node:20-slim` builder → `nginx:alpine` server
- nginx.conf.template placed at `/etc/nginx/templates/default.conf.template` — the `nginx:alpine` image auto-substitutes `${PORT}` from the environment on startup
- SPA `try_files $uri $uri/ /index.html` for client-side routing
- Cloud Run sets PORT=8080 by default
- The Dockerfile should NOT have a CMD — the base `nginx:alpine` image handles startup

**Node.js server** (Express, Fastify, Next.js SSR):
- Single-stage or multi-stage Dockerfile with `node:20-slim` runtime
- App must listen on `process.env.PORT`
- CMD should be `["node", "server.js"]` or equivalent

### 3. Gather deployment config from user

Ask the user for any values you can't infer. Present sensible defaults and let them confirm or override:
- **GCP Project** — ask if they want to use an existing project or create a new one. Note: managed projects like `gen-lang-client-*` (from Google AI Studio) often have org policy restrictions that block public access.
- **GCP region** for Artifact Registry (default: `us-west1`) — this is the registry region
- **Cloud Run deploy region** (can differ from registry region, e.g. `australia-southeast1`)
- **Service name** (default: derived from package.json `name` field)
- **Artifact Registry repo name** (default: `cloud-run-source-deploy`)
- **Build-time env vars** — only `VITE_*` or `NEXT_PUBLIC_*` vars that are actually used client-side
- **Runtime env vars** — server-side only vars. These are NOT baked into the image; they're set on the Cloud Run service at deploy time via `--set-env-vars`
- **Allow unauthenticated access?** (default: yes for public apps)
- **Custom domain?** — if the user has a custom domain, set up a Global HTTPS Load Balancer (see Section 7). Do NOT use `gcloud run domain-mappings` — it fails with `501 UNIMPLEMENTED` in many regions.

**Important distinction — build-time vs runtime vars:**
- Build-time vars (`--build-arg`) are embedded into the static JS bundle during `npm run build`. They cannot be changed without rebuilding. Use for `VITE_*` / `NEXT_PUBLIC_*` vars.
- Runtime vars (`--set-env-vars`) are available to the running container as `process.env.*`. Use for server-side secrets and config. For static SPAs, these are only useful if nginx or a sidecar reads them.

### 4. Generate/update deployment files

If deployment files already exist, **diff them against what you would generate** and ask the user before overwriting. Highlight what changed and why.

Create or update these files in the project root:

#### `.dockerignore`
```
node_modules
.git
.env*
dist
build
*.md
.claude
```

#### `Dockerfile`

For static SPA (Vite/React example):
```dockerfile
# Stage 1: Build the frontend
FROM node:20-slim AS builder

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci

# Copy the rest of the source code
COPY . .

# Build-time env vars — Vite embeds these into the static bundle during build.
# Each ARG must have a corresponding --build-arg in cloudbuild.yaml
# and a substitution variable (prefixed with _) in the Cloud Build trigger.
ARG VITE_CONVEX_URL
ENV VITE_CONVEX_URL=$VITE_CONVEX_URL

# Build the frontend (outputs to /app/dist by default)
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy the built static assets from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# nginx:alpine auto-processes *.template files in /etc/nginx/templates/
# on startup, substituting environment variables like $PORT.
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Cloud Run sets PORT=8080 by default
ENV PORT=8080
EXPOSE 8080

# No CMD needed — the base nginx image handles startup
```

**Adapt the template:**
- Replace `VITE_*` ARGs with actual env vars discovered in the project
- If using bun: replace `node:20-slim` with `oven/bun:1` and `npm ci` with `bun install --frozen-lockfile`
- If using pnpm: add `RUN corepack enable` before install, use `pnpm install --frozen-lockfile`
- If output dir is not `dist`, update the COPY path accordingly

#### `nginx.conf.template` (static SPA only)

```nginx
server {
    listen ${PORT};
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }

    # Error pages
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
```

**Note:** `${PORT}` is substituted by nginx's `envsubst` on startup. `$uri` is a native nginx variable — do NOT wrap it in `${}` or it will break.

#### `cloudbuild.yaml`

**IMPORTANT:** Use `${_TAG}` with a default of `latest` instead of `$COMMIT_SHA`. `$COMMIT_SHA` is only available when triggered by a repo event (push/PR). For manual `gcloud builds submit`, it will be empty and cause an "invalid image name" error.

```yaml
steps:
  # Build the container image using Dockerfile and pass build arguments
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'REGION-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/SERVICE_NAME:${_TAG}'
      # Pass the secrets/variables directly into the Docker build
      - '--build-arg'
      - 'VITE_CONVEX_URL=$_VITE_CONVEX_URL'
      - '.'

  # Push the container image to Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'REGION-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/SERVICE_NAME:${_TAG}']

  # Deploy container image to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'SERVICE_NAME'
      - '--image'
      - 'REGION-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/SERVICE_NAME:${_TAG}'
      - '--region'
      - 'DEPLOY_REGION'
      # Remove --allow-unauthenticated if the app requires auth
      - '--allow-unauthenticated'

# Substitution variables — set these in the Cloud Build trigger settings.
# Cloud Build provides $PROJECT_ID automatically.
# User-defined substitutions must be prefixed with _.
# _TAG defaults to 'latest' for manual builds; override with $COMMIT_SHA in triggers.
substitutions:
  _VITE_CONVEX_URL: ""
  _TAG: 'latest'

images:
  - 'REGION-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/SERVICE_NAME:${_TAG}'

options:
  logging: CLOUD_LOGGING_ONLY
```

**Adapt the template:**
- Replace `REGION` with the actual Artifact Registry region (e.g. `australia-southeast1`)
- Replace `DEPLOY_REGION` with the Cloud Run region (e.g. `australia-southeast1`)
- Replace `SERVICE_NAME` with the actual service name
- Replace the `--build-arg` entries with the actual build-time env vars
- If there are runtime vars, add `--set-env-vars` line before `--allow-unauthenticated`
- All substitution vars in the `substitutions:` block must match what's referenced in the steps

### 5. Post-generation: GCP project setup guide

After generating files, check if the user needs help setting up GCP. Include these steps:

#### New project setup (if needed)
```bash
# Create project
gcloud projects create PROJECT_NAME --name="Project Display Name"

# Set as active
gcloud config set project PROJECT_NAME

# Link billing (required for Cloud Run, Cloud Build, Artifact Registry)
gcloud billing accounts list
gcloud billing projects link PROJECT_NAME --billing-account=ACCOUNT_ID

# Enable required APIs (include compute if custom domain is needed)
gcloud services enable cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com compute.googleapis.com
```

#### IAM permissions for Cloud Build service account
The default Compute Engine service account (`PROJECT_NUMBER-compute@developer.gserviceaccount.com`) needs these roles. **Grant all of these upfront to avoid build failures:**

```bash
# Get the project number
PROJECT_NUMBER=$(gcloud projects describe PROJECT_NAME --format="value(projectNumber)")

# Storage access (for uploading build source)
gcloud projects add-iam-policy-binding PROJECT_NAME --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" --role="roles/storage.admin"

# Artifact Registry access (for pushing images)
gcloud projects add-iam-policy-binding PROJECT_NAME --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" --role="roles/artifactregistry.writer"

# Cloud Run deploy access
gcloud projects add-iam-policy-binding PROJECT_NAME --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" --role="roles/run.admin"

# Service account user (required to deploy to Cloud Run)
gcloud iam service-accounts add-iam-policy-binding ${PROJECT_NUMBER}-compute@developer.gserviceaccount.com --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" --role="roles/iam.serviceAccountUser" --project=PROJECT_NAME

# Logging (to see build logs)
gcloud projects add-iam-policy-binding PROJECT_NAME --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" --role="roles/logging.logWriter"
```

#### Create Artifact Registry repo (one-time)
```bash
gcloud artifacts repositories create cloud-run-source-deploy --repository-format=docker --location=REGION
```

#### Public access
After deploying, to allow unauthenticated access:
```bash
gcloud run services add-iam-policy-binding SERVICE_NAME --region=DEPLOY_REGION --member="allUsers" --role="roles/run.invoker"
```

**If you get org policy errors** (`FAILED_PRECONDITION: One or more users named in the policy do not belong to a permitted customer`):
- This means the GCP organization has `iam.allowedPolicyMemberDomains` constraint
- **Option 1:** Go to Cloud Run console → select the service → Security tab → change to "Allow unauthenticated invocations" (the UI sometimes bypasses policy)
- **Option 2:** Disable the constraint for the project:
  ```bash
  gcloud resource-manager org-policies disable-enforce iam.allowedPolicyMemberDomains --project=PROJECT_NAME
  ```
  Then retry the IAM binding.
- **Option 3:** Restrict to your domain only:
  ```bash
  gcloud run services add-iam-policy-binding SERVICE_NAME --region=DEPLOY_REGION --member="domain:yourdomain.com" --role="roles/run.invoker"
  ```
- **Note:** Managed projects like `gen-lang-client-*` (from Google AI Studio) often have org policies you cannot change. Create your own project instead.

### 6. Post-generation summary

After generating files, print a clear summary:

```
## Deployment files ready

**Service:** <service-name>
**Project:** <project-id>
**Artifact Registry:** <region>-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/<service-name>
**Deploy region:** <deploy-region>
**Strategy:** Static SPA (Vite + Nginx) / Node.js server

### Files created/updated:
- `Dockerfile` — multi-stage build (node:20-slim → nginx:alpine)
- `cloudbuild.yaml` — build, push, deploy pipeline
- `nginx.conf.template` — SPA routing config
- `.dockerignore` — excludes node_modules, .git, .env files

### Build-time variables (set in Cloud Build trigger → Substitution variables):
- `_VITE_CONVEX_URL` → passed as --build-arg, embedded in JS bundle

### Next steps:
1. Set up GCP project (if new) — see setup guide above
2. Grant IAM permissions to build service account
3. Create Artifact Registry repo
4. Submit build:
   gcloud builds submit --config cloudbuild.yaml
5. Enable public access (if needed)
```

### 7. Custom domain setup

If the user wants to point a custom domain to their Cloud Run service, set up a **Global HTTPS Load Balancer**. Do NOT use `gcloud run domain-mappings` — it is not supported in many regions (e.g. `australia-southeast1` returns `501 UNIMPLEMENTED`).

#### Enable Compute Engine API (required for load balancer)
```bash
gcloud services enable compute.googleapis.com --project=PROJECT_NAME
```
**Important:** After enabling, wait ~30 seconds before running compute commands — the API needs time to propagate. If you get `SERVICE_DISABLED` errors immediately after enabling, retry after a delay.

#### Step-by-step load balancer setup

Run these commands in order. Each must complete before the next.

```bash
# 1. Create a serverless Network Endpoint Group (NEG) pointing to the Cloud Run service
gcloud compute network-endpoint-groups create SERVICE_NAME-neg --region=DEPLOY_REGION --network-endpoint-type=serverless --cloud-run-service=SERVICE_NAME --project=PROJECT_NAME

# 2. Create a backend service
gcloud compute backend-services create SERVICE_NAME-backend --global --project=PROJECT_NAME

# 3. Add the NEG to the backend service
gcloud compute backend-services add-backend SERVICE_NAME-backend --global --network-endpoint-group=SERVICE_NAME-neg --network-endpoint-group-region=DEPLOY_REGION --project=PROJECT_NAME

# 4. Create a Google-managed SSL certificate for the domain
gcloud compute ssl-certificates create SERVICE_NAME-cert --domains=CUSTOM_DOMAIN --global --project=PROJECT_NAME

# 5. Reserve a global static IP address
gcloud compute addresses create SERVICE_NAME-ip --global --project=PROJECT_NAME

# 6. Get the IP address (user needs this for DNS)
gcloud compute addresses describe SERVICE_NAME-ip --global --project=PROJECT_NAME --format="value(address)"

# 7. Create a URL map routing all traffic to the backend
gcloud compute url-maps create SERVICE_NAME-urlmap --default-service=SERVICE_NAME-backend --global --project=PROJECT_NAME

# 8. Create the HTTPS target proxy
gcloud compute target-https-proxies create SERVICE_NAME-https-proxy --ssl-certificates=SERVICE_NAME-cert --url-map=SERVICE_NAME-urlmap --global --project=PROJECT_NAME

# 9. Create the HTTPS forwarding rule (port 443)
gcloud compute forwarding-rules create SERVICE_NAME-https-rule --global --target-https-proxy=SERVICE_NAME-https-proxy --address=SERVICE_NAME-ip --ports=443 --project=PROJECT_NAME
```

#### Set up HTTP → HTTPS redirect

```bash
# 1. Create a redirect-only URL map (write to temp file first since stdin doesn't work on Windows)
echo 'name: SERVICE_NAME-http-redirect
defaultUrlRedirect:
  redirectResponseCode: MOVED_PERMANENTLY_DEFAULT
  httpsRedirect: true' > /tmp/http-redirect.yaml

gcloud compute url-maps import SERVICE_NAME-http-redirect --global --project=PROJECT_NAME --source=/tmp/http-redirect.yaml

# 2. Create HTTP target proxy
gcloud compute target-http-proxies create SERVICE_NAME-http-proxy --url-map=SERVICE_NAME-http-redirect --global --project=PROJECT_NAME

# 3. Create HTTP forwarding rule (port 80)
gcloud compute forwarding-rules create SERVICE_NAME-http-rule --global --target-http-proxy=SERVICE_NAME-http-proxy --address=SERVICE_NAME-ip --ports=80 --project=PROJECT_NAME
```

#### DNS configuration

Tell the user to update their domain's DNS records at their registrar:

| Type | Host | Value |
|------|------|-------|
| A Record | @ | `<STATIC_IP from step 6>` |

If they have old A records (e.g. `216.239.x.x` from a previous Google domain mapping), those must be **removed** and replaced with the new IP.

Optional records to keep/add:
- **CNAME** `www` → `ghs.googlehosted.com.` (for www subdomain)
- **TXT** records for domain verification — keep these

#### SSL certificate provisioning

The managed SSL certificate starts in `PROVISIONING` status. It will become `ACTIVE` once:
1. DNS A record points to the load balancer IP
2. Google's certificate authority can reach the domain (15-60 minutes after DNS propagates)

Check status with:
```bash
gcloud compute ssl-certificates describe SERVICE_NAME-cert --global --project=PROJECT_NAME --format="yaml(managed)"
```

Status progression: `PROVISIONING` → `ACTIVE` (success) or `FAILED_NOT_VISIBLE` (DNS not yet propagated — wait and it will retry automatically).

Verify DNS is resolving correctly:
```bash
nslookup CUSTOM_DOMAIN 8.8.8.8
```

### 8. Deploying updates

To redeploy after code changes:
```bash
# Commit and push changes to git
git add -A && git commit -m "update" && git push

# Submit build (from project root)
gcloud builds submit --config cloudbuild.yaml
```

Or set up a Cloud Build trigger for auto-deploy on push.

## Important rules

- NEVER hardcode secrets or API keys in generated files — all sensitive values go through Cloud Build substitution variables (prefixed with `_`)
- Use `$PROJECT_ID` — Cloud Build provides this automatically, do not make it a substitution var
- Use `${_TAG}` instead of `$COMMIT_SHA` — COMMIT_SHA is empty on manual builds
- Preserve any existing deployment files the user has customized — diff and confirm before overwriting
- Adapt ALL templates to the actual project — use real env var names, real build commands, real output directories. Never leave placeholder names like `VITE_EXAMPLE_VAR`
- If the project uses `bun`, use `oven/bun:1` as the builder image and `bun install --frozen-lockfile`
- If the project uses `pnpm`, enable corepack and use `pnpm install --frozen-lockfile`
- The Artifact Registry region and Cloud Run deploy region can be different — always clarify both
- For static SPAs, the Dockerfile should have NO CMD — the nginx:alpine base image handles it
- In nginx.conf.template, `$uri` is a native nginx variable (no braces), while `${PORT}` uses braces for envsubst
- Only include env vars as build-time args if they are actually used in client-side code. Server-side-only keys (e.g. API keys used only in Convex/Express) should NOT be build args.
- When providing gcloud commands to the user, keep them on a **single line** — Cloud Shell and PowerShell both break on multi-line commands with backslash continuations
- NEVER use `gcloud run domain-mappings` — it returns `501 UNIMPLEMENTED` in many regions (e.g. `australia-southeast1`). Always use a Global HTTPS Load Balancer for custom domains.
- After enabling a GCP API with `gcloud services enable`, wait ~30 seconds before using it — the propagation delay causes `SERVICE_DISABLED` errors if you proceed immediately
- On Windows/Git Bash, `gcloud compute url-maps import --source=/dev/stdin` does NOT work. Write YAML to a temp file and use `--source=/tmp/file.yaml` instead
- When the org policy `iam.allowedPolicyMemberDomains` blocks `allUsers` bindings AND the user lacks org-admin rights to disable it, advise using the Cloud Run Console UI (Security tab) which can sometimes bypass the restriction

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `invalid image name "...:""` | `$COMMIT_SHA` empty on manual build | Use `${_TAG}` with default `latest` |
| `does not have storage.objects.get access` | Build SA missing storage role | Grant `roles/storage.admin` |
| `step exited with non-zero status: 1` on push step | Build SA missing AR write role | Grant `roles/artifactregistry.writer` |
| Deploy step fails silently | Build SA missing run.admin or iam.serviceAccountUser | Grant both roles |
| `One or more users named in the policy do not belong to a permitted customer` | Org policy blocks allUsers/allAuthenticatedUsers | Disable org policy constraint or use domain-restricted binding |
| `Billing account not found` | New project without billing | Link billing account |
| `API not enabled` | Required APIs not turned on | Enable cloudbuild, run, artifactregistry APIs |
| `Error: Forbidden` in browser | Cloud Run requires auth but no login flow | Set allUsers invoker role, or disable org policy first |
| `Creating domain mappings is not allowed in REGION` (501) | `gcloud run domain-mappings` not supported in that region | Use Global HTTPS Load Balancer instead (see Section 7) |
| `Compute Engine API has not been used` after enabling | API propagation delay | Wait 30 seconds after `gcloud services enable compute.googleapis.com` then retry |
| SSL cert stuck in `PROVISIONING` / `FAILED_NOT_VISIBLE` | DNS not yet pointing to load balancer IP | Verify A record with `nslookup DOMAIN 8.8.8.8`, wait 15-60 min after DNS update |
| `gcloud compute url-maps import` fails with stdin error | Windows/Git Bash doesn't support `/dev/stdin` | Write YAML to a temp file first, then pass with `--source=/tmp/file.yaml` |

## Storing secrets

Use Google Cloud Secret Manager for tokens and credentials:
```bash
# Store a secret (paste value then Ctrl+D)
gcloud secrets create SECRET_NAME --data-file=-

# Retrieve a secret
gcloud secrets versions access latest --secret=SECRET_NAME

# List all secrets
gcloud secrets list
```
