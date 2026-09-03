---
name: secret-manager
description: Manage secrets and credentials in Google Cloud Secret Manager - create, read, update, rotate and grant access to secrets, and wire them into Cloud Run services. Use when the user says "store a secret", "rotate a credential", "Secret Manager", "where do the API keys live", or needs a deployed workload to read a credential it must not hold on disk.
allowed-tools: Read, Glob, Grep, Bash
---

# Google Cloud Secret Manager — Password & Secret Management

You are helping the user manage secrets and credentials using **Google Cloud Secret Manager**.

## Quick Reference

### Store a new secret
```bash
gcloud secrets create SECRET_NAME --data-file=-
# Then paste the value and press Ctrl+D
```

Or from a file:
```bash
gcloud secrets create SECRET_NAME --data-file=path/to/file.txt
```

### Retrieve a secret
```bash
gcloud secrets versions access latest --secret=SECRET_NAME
```

### List all secrets
```bash
gcloud secrets list
```

### Update a secret (add new version)
```bash
gcloud secrets versions add SECRET_NAME --data-file=-
# Paste new value, press Ctrl+D
```

### Delete a secret
```bash
gcloud secrets delete SECRET_NAME
```

### View secret metadata (without revealing value)
```bash
gcloud secrets describe SECRET_NAME
```

### List versions of a secret
```bash
gcloud secrets versions list SECRET_NAME
```

### Access a specific version
```bash
gcloud secrets versions access VERSION_NUMBER --secret=SECRET_NAME
```

### Disable a version (keep but prevent access)
```bash
gcloud secrets versions disable VERSION_NUMBER --secret=SECRET_NAME
```

### Use in Cloud Run / Cloud Build
Reference secrets as environment variables in `cloudbuild.yaml`:
```yaml
availableSecrets:
  secretManager:
    - versionName: projects/$PROJECT_ID/secrets/SECRET_NAME/versions/latest
      env: 'MY_SECRET_ENV'

steps:
  - name: 'gcr.io/cloud-builders/docker'
    secretEnv: ['MY_SECRET_ENV']
```

Or set on a Cloud Run service:
```bash
gcloud run services update SERVICE_NAME \
  --set-secrets=ENV_VAR_NAME=SECRET_NAME:latest \
  --region=REGION
```

## User's stored secrets
- `github-pat` — GitHub Personal Access Token for repo access

## Security tips
- Never paste secrets directly into commands as arguments (they appear in shell history)
- Always use `--data-file=-` (stdin) or `--data-file=path` to pass secret values
- Rotate tokens regularly and add new versions rather than recreating
- If a secret is accidentally exposed (e.g. in chat logs), regenerate it immediately
