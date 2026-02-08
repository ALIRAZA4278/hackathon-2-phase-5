# Phase V Helm Charts Deployment Checklist

Use this checklist to verify and deploy the Phase V Cloud-Native AI Todo Platform.

## Pre-Deployment Verification

### File Structure Check
- [ ] All 9 Helm charts exist in `helm/` directory
  - [ ] `backend/`
  - [ ] `frontend/`
  - [ ] `consumers/reminder/`
  - [ ] `consumers/recurring/`
  - [ ] `consumers/audit/`
  - [ ] `consumers/notification/`
  - [ ] `infrastructure/redpanda/`
  - [ ] `infrastructure/redis/`
  - [ ] `infrastructure/observability/`
  - [ ] `todo-app/` (umbrella)

### Chart Completeness
Each chart should have:
- [ ] `Chart.yaml` (metadata)
- [ ] `values.yaml` (configuration)
- [ ] `templates/_helpers.tpl` (template helpers)
- [ ] `templates/*.yaml` (Kubernetes resources)

### Backend Dockerfile
- [ ] Multi-stage build implemented
- [ ] Non-root user created
- [ ] HEALTHCHECK directive present

## Environment Setup

### Kubernetes Cluster
- [ ] Cluster is accessible (`kubectl cluster-info`)
- [ ] Sufficient resources available
- [ ] Storage class available for PVCs

### Dapr Installation
```bash
# Install Dapr
dapr init -k

# Verify Dapr is running
kubectl get pods -n dapr-system
```
- [ ] Dapr control plane pods running
- [ ] Dapr sidecar injector active

### External Dependencies
- [ ] PostgreSQL database (Neon) accessible
- [ ] Database connection string available
- [ ] Gemini API key available
- [ ] Better Auth secret generated

## Helm Configuration

### Update Dependencies
```bash
cd helm/todo-app
helm dependency update
```
- [ ] Dependencies downloaded to `charts/` directory
- [ ] No errors during dependency update

### Configure Secrets
Create `helm/todo-app/values-local.yaml`:
```yaml
backend:
  secrets:
    databaseUrl: "postgresql://user:pass@host.neon.tech:5432/db?sslmode=require"
    geminiApiKey: "your-gemini-api-key-here"
    betterAuthSecret: "your-better-auth-secret-32-chars"

# Optional: Adjust resource limits
backend:
  resources:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 1000m
      memory: 1Gi
```
- [ ] `values-local.yaml` created
- [ ] Database URL is correct and tested
- [ ] API keys are valid
- [ ] File is NOT committed to git (gitignored)

### Validate Helm Charts
```bash
# Lint all charts
helm lint helm/backend
helm lint helm/frontend
helm lint helm/consumers/reminder
helm lint helm/consumers/recurring
helm lint helm/consumers/audit
helm lint helm/consumers/notification
helm lint helm/infrastructure/redpanda
helm lint helm/infrastructure/redis
helm lint helm/infrastructure/observability
helm lint helm/todo-app

# Dry-run installation
cd helm/todo-app
helm install todo-app . -f values-local.yaml --dry-run --debug
```
- [ ] All charts pass linting
- [ ] Dry-run produces valid YAML
- [ ] No template errors

## Deployment

### Install Release
```bash
cd helm/todo-app
helm install todo-app . -f values-local.yaml
```
- [ ] Installation completes successfully
- [ ] NOTES.txt displays post-install instructions

### Monitor Deployment
```bash
# Watch pods starting
kubectl get pods -w

# Check deployment status
kubectl get deployments
kubectl get statefulsets
kubectl get services
```
- [ ] All pods reach Running status
- [ ] Each app pod has 2 containers (app + daprd sidecar)
- [ ] All services have endpoints

### Verify Dapr Sidecars
```bash
# List containers per pod
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}'
```
Expected output for app pods:
- `todo-backend-xxx`: `todo-backend daprd`
- `todo-frontend-xxx`: `todo-frontend daprd`
- `reminder-consumer-xxx`: `reminder-consumer daprd`
- [ ] All app pods have daprd sidecar
- [ ] Infrastructure pods do NOT have sidecars (expected)

## Service Access Verification

### Frontend Access
```bash
# Get NodePort
export NODE_PORT=$(kubectl get svc todo-app-frontend -o jsonpath='{.spec.ports[0].nodePort}')
export NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[0].address}')
echo "Frontend: http://$NODE_IP:$NODE_PORT"
```
- [ ] Frontend loads in browser
- [ ] Can create an account
- [ ] Can log in

### Backend API
```bash
# Port-forward
kubectl port-forward svc/todo-app-backend 8000:8000

# Test health endpoint
curl http://localhost:8000/health
```
- [ ] Port-forward established
- [ ] `/health` endpoint returns 200 OK
- [ ] `/docs` (FastAPI docs) accessible

### Grafana Dashboard
```bash
# Access via NodePort (default: 32000)
echo "Grafana: http://$NODE_IP:32000"
# Login: admin / admin
```
- [ ] Grafana login page loads
- [ ] Can log in with admin credentials
- [ ] Prometheus data source is configured

### Prometheus Metrics
```bash
# Port-forward
kubectl port-forward svc/todo-app-observability-prometheus 9090:9090
# Visit: http://localhost:9090
```
- [ ] Prometheus UI accessible
- [ ] Targets page shows all services
- [ ] Metrics are being collected

## Functional Testing

### Todo Operations
- [ ] Create a new todo task
- [ ] View todo list
- [ ] Update a todo task
- [ ] Mark task as complete
- [ ] Delete a task

### AI Features
- [ ] Chat with AI assistant works
- [ ] AI suggestions are generated
- [ ] AI responses are contextual

### Event Processing
Monitor consumer logs:
```bash
kubectl logs -l app=reminder-consumer -f
kubectl logs -l app=recurring-consumer -f
kubectl logs -l app=audit-consumer -f
kubectl logs -l app=notification-consumer -f
```
- [ ] Consumers are receiving Kafka messages
- [ ] No error logs in consumers
- [ ] Events are being processed

## Monitoring Setup

### Prometheus Targets
Visit Prometheus → Status → Targets
- [ ] `todo-backend` target UP
- [ ] `reminder-consumer` target UP
- [ ] `recurring-consumer` target UP
- [ ] `audit-consumer` target UP
- [ ] `notification-consumer` target UP

### Grafana Dashboards
- [ ] Create dashboard for backend metrics
- [ ] Create dashboard for consumer metrics
- [ ] Set up alerts for critical metrics
- [ ] Configure notification channels

## Troubleshooting

### Pod Not Starting
```bash
# Describe pod
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>
kubectl logs <pod-name> -c daprd  # Dapr sidecar logs
```

### Database Connection Issues
```bash
# Verify secret
kubectl get secret todo-app-backend-secret -o yaml

# Decode DATABASE_URL
kubectl get secret todo-app-backend-secret -o jsonpath='{.data.DATABASE_URL}' | base64 -d
```

### Dapr Issues
```bash
# Check Dapr system
kubectl get pods -n dapr-system

# Restart pod to reinject sidecar
kubectl delete pod <pod-name>
```

## Production Readiness

### Security Hardening
- [ ] Change Grafana admin password
- [ ] Use external secret manager (not values.yaml)
- [ ] Enable TLS for all services
- [ ] Configure network policies
- [ ] Enable pod security policies

### High Availability
- [ ] Increase replica counts for critical services
- [ ] Configure pod anti-affinity
- [ ] Set up pod disruption budgets
- [ ] Enable horizontal pod autoscaling

### Monitoring & Alerting
- [ ] Set up Grafana alerts
- [ ] Configure PagerDuty/Slack notifications
- [ ] Create runbooks for common issues
- [ ] Document escalation procedures

### Backup & Disaster Recovery
- [ ] Configure Redpanda data backups
- [ ] Document database backup strategy
- [ ] Test disaster recovery procedures
- [ ] Create runbook for rollback

## Cleanup (If Needed)

### Uninstall Release
```bash
helm uninstall todo-app
```

### Clean Up Resources
```bash
# Delete PVCs
kubectl delete pvc -l app.kubernetes.io/instance=todo-app

# Verify all resources deleted
kubectl get all
```

## Success Criteria

All items below should be true for successful deployment:

- [x] All Helm charts created and validated
- [ ] All pods running and healthy
- [ ] Frontend accessible and functional
- [ ] Backend API responding
- [ ] Dapr sidecars injected correctly
- [ ] Consumers processing events
- [ ] Prometheus collecting metrics
- [ ] Grafana dashboards accessible
- [ ] No error logs in any service
- [ ] All functional tests passing

---

**Date**: _______________
**Deployed By**: _______________
**Environment**: _______________
**Release Name**: _______________
**Namespace**: _______________
