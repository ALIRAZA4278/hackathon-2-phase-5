# CI/CD Pipeline Documentation

## Overview

The GitHub Actions CI/CD pipeline (`ci-cd.yaml`) implements a secure, five-stage deployment workflow for the AI Todo Platform with automatic rollback capabilities.

## Pipeline Stages

### Stage 1: Build Images
- Builds container images for all services using Docker Buildx
- Tags images with commit SHA for traceability
- Uses GitHub Actions cache for faster builds
- **Services built**: backend, frontend, reminder-consumer, recurring-consumer, audit-consumer, notification-consumer

### Stage 2: Security Scanning (scan)
- Runs Trivy vulnerability scanner on backend and frontend
- Scans for CRITICAL and HIGH severity vulnerabilities
- Currently set to `exit-code: 0` (non-blocking) to allow workflow to continue
- Security reports are available in the Actions logs

### Stage 3: Run Tests (test)
- Backend: Python 3.11 environment, dependency installation, import validation
- Frontend: Node.js 20 environment, dependency installation, TypeScript type checking
- Tests run in parallel after build completes

### Stage 4: Push to Registry (push)
- Only runs on push to `main` branch (not on PRs)
- Pushes images to GitHub Container Registry (ghcr.io)
- Tags each image with both commit SHA and `latest`
- Requires successful test and scan stages

### Stage 5: Helm Deploy (deploy)
- Deploys to Azure Kubernetes Service (AKS) using Helm
- Uses `helm upgrade --install` with `--wait` and `--timeout 5m`
- Updates all service images to the commit SHA tag
- Runs smoke tests to verify deployment health
- Only runs after successful push to registry

### Rollback Stage
- Automatically triggered if deploy stage fails
- Uses `helm rollback todo-app 0` to revert to previous release
- Waits for rollback completion with 3-minute timeout

## Required GitHub Secrets

The pipeline requires the following secrets to be configured in your GitHub repository:

| Secret Name | Description | Usage |
|-------------|-------------|-------|
| `GITHUB_TOKEN` | Automatically provided by GitHub Actions | Push images to GHCR |
| `AZURE_CREDENTIALS` | Azure service principal credentials (JSON) | Authenticate to Azure |
| `AKS_RESOURCE_GROUP` | Azure resource group name | Connect to AKS cluster |
| `AKS_CLUSTER_NAME` | AKS cluster name | Deploy to Kubernetes |

### Setting Up Azure Credentials

To create the Azure service principal for `AZURE_CREDENTIALS`:

```bash
az ad sp create-for-rbac \
  --name "github-actions-todo-app" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group} \
  --sdk-auth
```

The output JSON should be added as the `AZURE_CREDENTIALS` secret.

## Environment Variables

All configuration uses environment variables - NO secrets are hardcoded. The pipeline uses:

- `REGISTRY`: GitHub Container Registry URL (ghcr.io)
- `*_IMAGE`: Image names constructed from repository name
- Image tags: Commit SHA and `latest`

## Workflow Triggers

- **Push to main**: Runs full pipeline including deployment
- **Pull Request to main**: Runs build, test, and scan stages only (no push/deploy)

## Rollback Procedures

### Automatic Rollback
If the deploy stage fails, the rollback job automatically reverts to the previous Helm release.

### Manual Rollback

To manually rollback to a specific release:

```bash
# List release history
helm history todo-app

# Rollback to specific revision
helm rollback todo-app [REVISION]

# Rollback to previous release
helm rollback todo-app 0
```

### Emergency Rollback from Local Machine

If you need to rollback manually:

1. Authenticate to Azure:
   ```bash
   az login
   az aks get-credentials --resource-group {RG} --name {CLUSTER}
   ```

2. Perform rollback:
   ```bash
   helm rollback todo-app 0 --wait --timeout 3m
   ```

3. Verify health:
   ```bash
   kubectl get pods -l app=todo-backend
   kubectl get pods -l app=todo-frontend
   ```

## Security Best Practices

1. **No Hardcoded Secrets**: All credentials are stored in GitHub Secrets or Azure Key Vault
2. **Vulnerability Scanning**: Trivy scans every build for known CVEs
3. **Least Privilege**: Service principal has minimal required permissions
4. **Signed Images**: Images are tagged with commit SHA for auditability
5. **Environment Isolation**: Production deployments require manual approval via GitHub Environments

## Health Checks

The pipeline verifies deployment health by:

1. Waiting for Helm chart deployment to complete (`--wait` flag)
2. Checking pod readiness for backend and frontend (120s timeout)
3. If checks fail, automatic rollback is triggered

## Observability

After deployment, the following observability features are available:

- **Metrics**: Backend exposes `/metrics` endpoint for Prometheus
- **Logs**: Structured JSON logs from all services
- **Health**: `/health` endpoint on backend and frontend

## Troubleshooting

### Build Failures
- Check Dockerfile syntax and build context
- Verify all dependencies are in requirements.txt/package.json
- Review build logs in GitHub Actions

### Test Failures
- Review test output in the test job logs
- Backend import errors indicate missing dependencies or syntax errors
- Frontend type errors indicate TypeScript issues

### Scan Failures
- Review Trivy output for specific CVEs
- Update vulnerable dependencies
- Consider accepting risk for false positives (document in ADR)

### Deploy Failures
- Check Helm chart syntax: `helm lint helm/todo-app/`
- Verify AKS credentials and cluster accessibility
- Review pod logs: `kubectl logs -l app=todo-backend`
- Check resource limits and quota

### Rollback Failures
- Verify previous release exists: `helm history todo-app`
- Check cluster health: `kubectl get nodes`
- Manually intervene if automatic rollback fails

## Pipeline Customization

To modify the pipeline:

1. Edit `.github/workflows/ci-cd.yaml`
2. Test changes on a feature branch first
3. Use `pull_request` trigger to validate changes without deployment
4. Document significant changes in an ADR

## Future Enhancements

- Add integration tests to test stage
- Implement canary deployments (gradual rollout)
- Add Slack/email notifications for deployment status
- Implement environment promotion (dev → staging → production)
- Add DAST (Dynamic Application Security Testing)
- Implement container image signing with Cosign
