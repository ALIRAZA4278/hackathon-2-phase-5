# CI/CD Environment Variables Documentation

## Overview

This document lists all environment variables and secrets used in the CI/CD pipeline. **CRITICAL**: Never hardcode secrets or credentials in any pipeline file.

## Pipeline Environment Variables

These are defined in the `env` section of `.github/workflows/ci-cd.yaml`:

| Variable | Value | Purpose |
|----------|-------|---------|
| `REGISTRY` | `ghcr.io` | GitHub Container Registry base URL |
| `BACKEND_IMAGE` | `ghcr.io/${{ github.repository }}/backend` | Backend service image name |
| `FRONTEND_IMAGE` | `ghcr.io/${{ github.repository }}/frontend` | Frontend service image name |
| `REMINDER_IMAGE` | `ghcr.io/${{ github.repository }}/reminder-consumer` | Reminder consumer image name |
| `RECURRING_IMAGE` | `ghcr.io/${{ github.repository }}/recurring-consumer` | Recurring task consumer image name |
| `AUDIT_IMAGE` | `ghcr.io/${{ github.repository }}/audit-consumer` | Audit log consumer image name |
| `NOTIFICATION_IMAGE` | `ghcr.io/${{ github.repository }}/notification-consumer` | Notification consumer image name |

## GitHub Actions Automatic Variables

These are provided automatically by GitHub Actions:

| Variable | Example | Purpose |
|----------|---------|---------|
| `github.sha` | `abc123def456...` | Commit SHA for image tagging |
| `github.ref` | `refs/heads/main` | Git reference being built |
| `github.event_name` | `push` or `pull_request` | Trigger event type |
| `github.repository` | `username/repo` | Repository name |
| `github.actor` | `username` | User who triggered the workflow |

## Required GitHub Secrets

These must be configured in repository Settings → Secrets and variables → Actions:

### 1. GITHUB_TOKEN
- **Type**: Automatically provided
- **Purpose**: Authenticate to GitHub Container Registry
- **Permissions**: `contents: read`, `packages: write`
- **Setup**: No action needed (automatic)
- **Used in**: `push` job for `docker/login-action`

### 2. AZURE_CREDENTIALS
- **Type**: JSON object
- **Purpose**: Authenticate to Azure services
- **Format**:
  ```json
  {
    "clientId": "<service-principal-client-id>",
    "clientSecret": "<service-principal-secret>",
    "subscriptionId": "<azure-subscription-id>",
    "tenantId": "<azure-tenant-id>"
  }
  ```
- **Setup**:
  ```bash
  az ad sp create-for-rbac \
    --name "github-actions-todo-app" \
    --role contributor \
    --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group} \
    --sdk-auth
  ```
- **Used in**: `deploy` and `rollback` jobs for `azure/login@v1`

### 3. AKS_RESOURCE_GROUP
- **Type**: String
- **Purpose**: Azure resource group containing the AKS cluster
- **Example**: `todo-app-rg`
- **Setup**: Create resource group in Azure, add name as secret
- **Used in**: `deploy` and `rollback` jobs for `azure/aks-set-context@v3`

### 4. AKS_CLUSTER_NAME
- **Type**: String
- **Purpose**: Name of the AKS cluster
- **Example**: `todo-app-aks`
- **Setup**: Create AKS cluster in Azure, add name as secret
- **Used in**: `deploy` and `rollback` jobs for `azure/aks-set-context@v3`

## Application Environment Variables

These are **NOT** stored in the pipeline - they should be in Kubernetes Secrets or Azure Key Vault:

### Backend Application
| Variable | Purpose | Storage |
|----------|---------|---------|
| `DATABASE_URL` | Neon PostgreSQL connection string | Kubernetes Secret |
| `BETTER_AUTH_SECRET` | JWT verification secret | Kubernetes Secret |
| `FRONTEND_URL` | Frontend URL for CORS | ConfigMap |
| `GOOGLE_GEMINI_API_KEY` | AI chatbot API key | Kubernetes Secret |
| `REDIS_HOST` | Redis cache host | ConfigMap |
| `REDIS_PORT` | Redis cache port | ConfigMap |

### Frontend Application
| Variable | Purpose | Storage |
|----------|---------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | ConfigMap |
| `BETTER_AUTH_SECRET` | Auth secret (server-side) | Kubernetes Secret |
| `DATABASE_URL` | Database connection | Kubernetes Secret |

### Consumer Services
| Variable | Purpose | Storage |
|----------|---------|---------|
| `DATABASE_URL` | Database connection | Kubernetes Secret |
| `REDIS_HOST` | Redis host | ConfigMap |
| `REDIS_PORT` | Redis port | ConfigMap |
| `APP_ID` | Dapr application ID | ConfigMap |

## Helm Chart Values

These are passed via `--set` flags during deployment:

| Value | Example | Purpose |
|-------|---------|---------|
| `backend.image.tag` | `abc123def456` | Backend image version |
| `frontend.image.tag` | `abc123def456` | Frontend image version |
| `reminder.image.tag` | `abc123def456` | Reminder consumer version |
| `recurring.image.tag` | `abc123def456` | Recurring consumer version |
| `audit.image.tag` | `abc123def456` | Audit consumer version |
| `notification.image.tag` | `abc123def456` | Notification consumer version |

## Setup Checklist

Before running the pipeline, ensure:

- [ ] `AZURE_CREDENTIALS` secret created with valid service principal
- [ ] `AKS_RESOURCE_GROUP` secret contains correct resource group name
- [ ] `AKS_CLUSTER_NAME` secret contains correct cluster name
- [ ] Service principal has `Contributor` role on resource group
- [ ] AKS cluster is accessible and running
- [ ] Kubernetes secrets created for application credentials
- [ ] Helm chart exists at `helm/todo-app/`
- [ ] GitHub Container Registry permissions configured

## Security Best Practices

1. **Rotate Secrets Regularly**: Update service principal credentials quarterly
2. **Principle of Least Privilege**: Grant only necessary permissions
3. **Audit Access**: Review GitHub Actions logs for unauthorized access
4. **Separate Environments**: Use different secrets for dev/staging/production
5. **No Secrets in Logs**: Mask sensitive values in workflow output
6. **Use Key Vault**: Store application secrets in Azure Key Vault, not ConfigMaps

## Debugging Variables

To debug variable values in the pipeline (without exposing secrets):

```yaml
- name: Debug Variables
  run: |
    echo "Repository: ${{ github.repository }}"
    echo "Commit SHA: ${{ github.sha }}"
    echo "Branch: ${{ github.ref }}"
    echo "Event: ${{ github.event_name }}"
    # NEVER echo secrets!
```

## References

- [GitHub Actions Environment Variables](https://docs.github.com/en/actions/learn-github-actions/environment-variables)
- [GitHub Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Azure Service Principals](https://learn.microsoft.com/en-us/azure/aks/kubernetes-service-principal)
- [Helm Values Files](https://helm.sh/docs/chart_template_guide/values_files/)
