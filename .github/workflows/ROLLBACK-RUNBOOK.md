# Rollback Runbook

## Overview

This runbook provides step-by-step procedures for rolling back deployments of the AI Todo Platform. Use this when a deployment causes issues in production.

## When to Rollback

Consider rollback when:
- Critical bugs are discovered in production
- Performance degradation is observed
- Security vulnerabilities are detected
- Health checks are failing
- User-reported critical issues spike
- Database migrations fail

## Automatic Rollback

The CI/CD pipeline includes automatic rollback triggered when the deploy stage fails.

### How It Works

1. Deploy job fails (pod not ready, timeout, health check failure)
2. Rollback job automatically triggers
3. `helm rollback todo-app 0` reverts to previous release
4. Waits for rollback to complete (3-minute timeout)
5. Outputs "Rollback completed" message

### Monitoring Automatic Rollback

1. Go to GitHub Actions tab in repository
2. Click on the failed workflow run
3. Check the "rollback" job status
4. Review logs for confirmation

## Manual Rollback Procedures

### Procedure 1: Quick Rollback (Previous Release)

**When to use**: Need to immediately revert to the last working version

**Prerequisites**:
- Azure CLI installed and authenticated
- kubectl configured for AKS cluster
- Helm installed

**Steps**:

1. Authenticate to Azure:
   ```bash
   az login
   az account set --subscription <subscription-id>
   ```

2. Get AKS credentials:
   ```bash
   az aks get-credentials \
     --resource-group <resource-group-name> \
     --name <cluster-name>
   ```

3. Verify current release status:
   ```bash
   helm list -n default
   helm status todo-app
   ```

4. Check release history:
   ```bash
   helm history todo-app
   ```
   Output example:
   ```
   REVISION  UPDATED                   STATUS      CHART           DESCRIPTION
   1         Fri Feb 7 10:00:00 2026   superseded  todo-app-1.0.0  Install complete
   2         Fri Feb 7 14:00:00 2026   deployed    todo-app-1.0.1  Upgrade complete
   ```

5. Rollback to previous release:
   ```bash
   helm rollback todo-app 0 --wait --timeout 3m
   ```
   The `0` means "previous release" (revision 1 in example above)

6. Verify rollback success:
   ```bash
   kubectl get pods -l app=todo-backend
   kubectl get pods -l app=todo-frontend
   ```
   Expected: All pods in `Running` state with `READY 1/1`

7. Run smoke test:
   ```bash
   kubectl run curl-test --image=curlimages/curl:latest --rm -it --restart=Never -- \
     curl http://todo-backend-service/health
   ```
   Expected: `{"status":"healthy","service":"hackathon-todo-api"}`

8. Document the rollback:
   - Create incident ticket
   - Update status page
   - Notify stakeholders

### Procedure 2: Rollback to Specific Revision

**When to use**: Need to revert to a specific known-good version (not just previous)

**Steps**:

1. Authenticate and get credentials (same as Procedure 1, steps 1-2)

2. View release history:
   ```bash
   helm history todo-app --max 10
   ```

3. Identify target revision:
   - Look for `STATUS: deployed` on a working version
   - Note the REVISION number

4. Rollback to specific revision:
   ```bash
   helm rollback todo-app <REVISION> --wait --timeout 5m
   ```
   Example: `helm rollback todo-app 3 --wait --timeout 5m`

5. Verify rollback (same as Procedure 1, steps 6-8)

### Procedure 3: Emergency Rollback (Direct Kubernetes)

**When to use**: Helm is unavailable or broken

**WARNING**: This procedure bypasses Helm tracking. Use only in emergencies.

**Steps**:

1. Authenticate and get credentials (same as Procedure 1, steps 1-2)

2. Scale down current deployment:
   ```bash
   kubectl scale deployment todo-backend --replicas=0
   kubectl scale deployment todo-frontend --replicas=0
   kubectl scale deployment reminder-consumer --replicas=0
   kubectl scale deployment recurring-consumer --replicas=0
   kubectl scale deployment audit-consumer --replicas=0
   kubectl scale deployment notification-consumer --replicas=0
   ```

3. Update image tags to previous version:
   ```bash
   # Find previous working commit SHA from GitHub or container registry
   export PREVIOUS_TAG="abc123def456"

   kubectl set image deployment/todo-backend \
     backend=ghcr.io/<repo>/backend:$PREVIOUS_TAG
   kubectl set image deployment/todo-frontend \
     frontend=ghcr.io/<repo>/frontend:$PREVIOUS_TAG
   kubectl set image deployment/reminder-consumer \
     consumer=ghcr.io/<repo>/reminder-consumer:$PREVIOUS_TAG
   kubectl set image deployment/recurring-consumer \
     consumer=ghcr.io/<repo>/recurring-consumer:$PREVIOUS_TAG
   kubectl set image deployment/audit-consumer \
     consumer=ghcr.io/<repo>/audit-consumer:$PREVIOUS_TAG
   kubectl set image deployment/notification-consumer \
     consumer=ghcr.io/<repo>/notification-consumer:$PREVIOUS_TAG
   ```

4. Scale up deployments:
   ```bash
   kubectl scale deployment todo-backend --replicas=2
   kubectl scale deployment todo-frontend --replicas=2
   kubectl scale deployment reminder-consumer --replicas=1
   kubectl scale deployment recurring-consumer --replicas=1
   kubectl scale deployment audit-consumer --replicas=1
   kubectl scale deployment notification-consumer --replicas=1
   ```

5. Wait for pods to be ready:
   ```bash
   kubectl wait --for=condition=ready pod -l app=todo-backend --timeout=120s
   kubectl wait --for=condition=ready pod -l app=todo-frontend --timeout=120s
   ```

6. Verify health (same as Procedure 1, steps 6-8)

7. **CRITICAL**: Reconcile Helm state:
   ```bash
   # Once system is stable, re-run helm upgrade to sync state
   helm upgrade --install todo-app helm/todo-app/ \
     --set backend.image.tag=$PREVIOUS_TAG \
     --set frontend.image.tag=$PREVIOUS_TAG
   ```

## Database Rollback

**WARNING**: Database rollbacks are HIGH RISK. Always coordinate with DBA.

### Procedure: Rollback Database Migration

1. Identify the migration that needs rollback:
   ```bash
   kubectl exec -it deployment/todo-backend -- \
     alembic current
   ```

2. Check migration history:
   ```bash
   kubectl exec -it deployment/todo-backend -- \
     alembic history
   ```

3. Rollback one migration:
   ```bash
   kubectl exec -it deployment/todo-backend -- \
     alembic downgrade -1
   ```

4. Verify schema:
   ```bash
   kubectl exec -it deployment/todo-backend -- \
     python -c "from app.db import engine; print(engine.table_names())"
   ```

5. Restart backend pods to pick up schema changes:
   ```bash
   kubectl rollout restart deployment/todo-backend
   ```

## Post-Rollback Checklist

After any rollback, complete the following:

- [ ] Verify all pods are running and healthy
- [ ] Run smoke tests against all critical endpoints
- [ ] Check application logs for errors
- [ ] Monitor Prometheus metrics for anomalies
- [ ] Verify database connections are working
- [ ] Test one user workflow end-to-end
- [ ] Update status page with resolution
- [ ] Create incident report document
- [ ] Schedule postmortem meeting
- [ ] Identify root cause of failed deployment
- [ ] Create tasks to prevent recurrence

## Rollback Verification Tests

Run these tests after rollback to confirm system health:

### Backend Health
```bash
kubectl run curl-test --image=curlimages/curl:latest --rm -it --restart=Never -- \
  curl http://todo-backend-service/health
```
Expected: `{"status":"healthy","service":"hackathon-todo-api"}`

### Frontend Health
```bash
kubectl run curl-test --image=curlimages/curl:latest --rm -it --restart=Never -- \
  curl http://todo-frontend-service/
```
Expected: HTTP 200 response

### Database Connectivity
```bash
kubectl exec -it deployment/todo-backend -- \
  python -c "from app.db import engine; engine.execute('SELECT 1')"
```
Expected: No errors

### Redis Connectivity
```bash
kubectl exec -it deployment/todo-backend -- \
  python -c "import redis; r=redis.Redis(host='redis-service'); r.ping()"
```
Expected: `True`

## Troubleshooting Rollback Failures

### Issue: Helm rollback times out

**Solution**:
```bash
# Increase timeout
helm rollback todo-app 0 --wait --timeout 10m

# Or skip wait
helm rollback todo-app 0 --no-hooks
```

### Issue: Pods stuck in ImagePullBackOff

**Cause**: Previous image no longer exists in registry

**Solution**:
```bash
# Check available tags
az acr repository show-tags --name <registry> --repository backend

# Rollback to a revision with available images
helm rollback todo-app <working-revision>
```

### Issue: Database migration incompatibility

**Cause**: Schema changed in new version, incompatible with old code

**Solution**:
```bash
# Must rollback database first (see Database Rollback section)
# Then rollback application
```

### Issue: Insufficient permissions

**Cause**: Service principal lacks required permissions

**Solution**:
```bash
# Grant Contributor role
az role assignment create \
  --assignee <service-principal-id> \
  --role Contributor \
  --scope /subscriptions/<sub>/resourceGroups/<rg>
```

## Communication Templates

### Incident Notification

```
INCIDENT: Production deployment rollback initiated

Time: [timestamp]
Environment: Production
Release: [version]
Reason: [brief description]
Impact: [services affected]
Action: Rolling back to [previous version]
ETA: [estimated time]
Status: [In Progress/Complete]
```

### Rollback Complete Notification

```
RESOLVED: Production rollback completed successfully

Previous Release: [version]
Rolled Back To: [version]
Rollback Time: [duration]
Current Status: All services healthy
Next Steps: [postmortem scheduled, fix in progress, etc.]
```

## Emergency Contacts

| Role | Name | Contact |
|------|------|---------|
| DevOps Lead | [Name] | [Phone/Slack] |
| Backend Lead | [Name] | [Phone/Slack] |
| DBA | [Name] | [Phone/Slack] |
| Product Manager | [Name] | [Phone/Slack] |
| On-Call Engineer | [Name] | [Phone/Slack] |

## Related Documents

- [CI/CD Pipeline Documentation](./.github/workflows/README.md)
- [Environment Variables](./VARIABLES.md)
- [Helm Chart Documentation](../../helm/todo-app/README.md)
- [Incident Response Playbook](./INCIDENT-RESPONSE.md)
