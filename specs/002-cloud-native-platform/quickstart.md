# Quickstart: Phase V — Cloud-Native AI Todo Platform

**Branch**: `002-cloud-native-platform` | **Date**: 2026-02-07

## Prerequisites

- Docker Desktop (with Kubernetes support)
- Minikube
- Helm 3.x
- Dapr CLI
- kubectl
- Node.js 20+
- Python 3.11+
- GitHub account (for CI/CD)

## Local Development Setup

### 1. Clone and checkout branch

```bash
git checkout 002-cloud-native-platform
```

### 2. Start Minikube

```bash
minikube start --memory=8192 --cpus=4
```

### 3. Initialize Dapr on cluster

```bash
dapr init --kubernetes --wait
```

### 4. Deploy infrastructure (Redpanda + Redis)

```bash
helm install redpanda helm/infrastructure/redpanda/
helm install redis helm/infrastructure/redis/
```

### 5. Apply Dapr components

```bash
kubectl apply -f dapr/components/
```

### 6. Deploy application services

```bash
helm install todo-backend helm/backend/
helm install todo-frontend helm/frontend/
helm install todo-consumers helm/consumers/
```

Or use the umbrella chart:

```bash
helm install todo-app helm/todo-app/
```

### 7. Access the application

```bash
minikube service todo-frontend --url
```

### 8. Deploy observability (optional)

```bash
helm install observability helm/infrastructure/observability/
```

## Environment Variables

### Backend

| Variable | Description | Source |
|----------|-------------|--------|
| DATABASE_URL | Neon PostgreSQL connection | K8s Secret |
| GEMINI_API_KEY | AI model API key | K8s Secret |
| BETTER_AUTH_SECRET | JWT signing secret | K8s Secret |
| FRONTEND_URL | Frontend URL for CORS | ConfigMap |

### Frontend

| Variable | Description | Source |
|----------|-------------|--------|
| NEXT_PUBLIC_API_URL | Backend API URL | ConfigMap |

## Validation Checklist

- [ ] All pods in Running state: `kubectl get pods`
- [ ] Frontend accessible via browser
- [ ] Can create task with priority and tags
- [ ] Can search and filter tasks
- [ ] AI chatbot responds to commands
- [ ] Events visible in Redpanda console
- [ ] Dapr dashboard accessible: `dapr dashboard -k`
- [ ] Prometheus metrics available
- [ ] Grafana dashboards loaded

## Cloud Deployment (AKS)

```bash
# Authenticate to AKS
az aks get-credentials --resource-group <rg> --name <cluster>

# Initialize Dapr
dapr init --kubernetes --wait

# Deploy via CI/CD (push to main)
git push origin main
# GitHub Actions handles: build → test → scan → push → deploy
```

## Troubleshooting

```bash
# Check pod logs
kubectl logs -f deployment/todo-backend -c todo-backend

# Check Dapr sidecar logs
kubectl logs -f deployment/todo-backend -c daprd

# AI-assisted diagnosis
kubectl-ai "why is the backend pod crashing?"

# Check Dapr components
dapr components -k

# Verify pub/sub
dapr publish --publish-app-id todo-backend --pubsub pubsub --topic todo.events --data '{"test": true}'
```
