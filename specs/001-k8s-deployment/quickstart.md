# Quickstart: Local Kubernetes Deployment

**Feature**: 001-k8s-deployment
**Date**: 2026-01-23
**Time to Complete**: ~15 minutes (first run), ~5 minutes (subsequent)

## Prerequisites

Before starting, ensure you have:

- [ ] Docker Desktop installed and running
- [ ] Docker AI Agent (Gordon) enabled
- [ ] Minikube installed
- [ ] kubectl installed
- [ ] Helm 3.x installed
- [ ] kubectl-ai installed (optional, for AI operations)
- [ ] Kagent installed (optional, for cluster analysis)

## Quick Deployment Steps

### 1. Start Minikube

```bash
# Start Minikube with Docker driver
minikube start --driver=docker

# Verify cluster is running
minikube status
kubectl get nodes
```

### 2. Configure Docker Environment

```bash
# Point your shell to Minikube's Docker daemon
# On Linux/macOS:
eval $(minikube docker-env)

# On Windows PowerShell:
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# On Windows CMD:
@FOR /f "tokens=*" %i IN ('minikube -p minikube docker-env --shell cmd') DO @%i
```

### 3. Build Docker Images

```bash
# Build frontend image
docker build -t todo-frontend:1.0.0 ./frontend

# Build backend image
docker build -t todo-backend:1.0.0 ./backend

# Verify images are available
minikube image ls | grep todo
```

### 4. Create Secrets File

Create `helm/backend/values-local.yaml` (this file is gitignored):

```yaml
# DO NOT COMMIT THIS FILE
secrets:
  databaseUrl: "your-neon-database-url"
  geminiApiKey: "your-gemini-api-key"
  betterAuthSecret: "your-jwt-secret"
```

### 5. Deploy with Helm

```bash
# Deploy backend first (frontend depends on it)
helm install backend ./helm/backend -f ./helm/backend/values-local.yaml

# Deploy frontend
helm install frontend ./helm/frontend

# Check deployment status
kubectl get pods
kubectl get services
```

### 6. Access the Application

```bash
# Get the frontend URL
minikube service frontend --url

# Open in browser (or copy URL)
minikube service frontend
```

## Verification Checklist

After deployment, verify:

- [ ] `kubectl get pods` shows all pods as Running
- [ ] `kubectl get services` shows frontend (NodePort) and backend (ClusterIP)
- [ ] Frontend loads in browser at Minikube service URL
- [ ] Login works (Better Auth)
- [ ] AI chatbot responds to messages
- [ ] Tasks can be created and listed

## Common Commands

### View Pod Logs

```bash
# Frontend logs
kubectl logs -l app=todo-frontend

# Backend logs
kubectl logs -l app=todo-backend

# Follow logs in real-time
kubectl logs -f -l app=todo-backend
```

### Scale Deployment

```bash
# Scale frontend to 3 replicas
kubectl scale deployment frontend --replicas=3

# Or via Helm
helm upgrade frontend ./helm/frontend --set replicaCount=3
```

### Check Pod Health

```bash
# Describe pod for events and status
kubectl describe pod -l app=todo-backend

# Get pod events
kubectl get events --sort-by='.lastTimestamp'
```

### Restart Deployment

```bash
# Rolling restart
kubectl rollout restart deployment frontend
kubectl rollout restart deployment backend

# Watch rollout status
kubectl rollout status deployment frontend
```

### Upgrade Application

```bash
# After changing values.yaml or rebuilding images
helm upgrade frontend ./helm/frontend
helm upgrade backend ./helm/backend -f ./helm/backend/values-local.yaml
```

### Rollback Application

```bash
# View release history
helm history frontend

# Rollback to previous version
helm rollback frontend 1
```

### Uninstall Application

```bash
# Remove Helm releases
helm uninstall frontend
helm uninstall backend

# Stop Minikube (optional)
minikube stop
```

## AI-Assisted Operations (Optional)

### Using kubectl-ai

```bash
# Natural language queries
kubectl-ai "show all pods in the cluster"
kubectl-ai "why is the backend pod failing"
kubectl-ai "scale frontend to 2 replicas"
kubectl-ai "show logs from backend pod"
```

### Using Kagent

```bash
# Cluster health analysis
kagent analyze

# Resource recommendations
kagent optimize

# Deployment verification
kagent verify deployment frontend
```

## Troubleshooting

### Pods Stuck in Pending

```bash
# Check events
kubectl get events

# Check if Minikube has enough resources
minikube ssh -- df -h
minikube ssh -- free -m
```

### Image Pull Errors

```bash
# Ensure you're using Minikube's Docker
eval $(minikube docker-env)

# Rebuild image
docker build -t todo-frontend:1.0.0 ./frontend

# Check image is available
minikube image ls | grep todo
```

### Pod CrashLoopBackOff

```bash
# Check logs
kubectl logs -l app=todo-backend --previous

# Check environment variables
kubectl describe pod -l app=todo-backend | grep -A 20 Environment
```

### Service Not Accessible

```bash
# Check service exists
kubectl get svc

# Test internal connectivity
kubectl run test --image=busybox --rm -it -- wget -qO- http://backend:8000/health

# Check Minikube tunnel (if using LoadBalancer)
minikube tunnel
```

### Database Connection Failed

```bash
# Verify secret is created
kubectl get secret

# Check DATABASE_URL is set
kubectl exec -it $(kubectl get pod -l app=todo-backend -o name | head -1) -- env | grep DATABASE

# Test connectivity from pod
kubectl exec -it $(kubectl get pod -l app=todo-backend -o name | head -1) -- python -c "import psycopg2; print('OK')"
```

## Environment Variables Reference

### Frontend

| Variable | Description | Source |
|----------|-------------|--------|
| NEXT_PUBLIC_API_URL | Backend API URL | ConfigMap |
| NODE_ENV | Environment mode | values.yaml |

### Backend

| Variable | Description | Source |
|----------|-------------|--------|
| DATABASE_URL | Neon PostgreSQL connection | Secret |
| GEMINI_API_KEY | AI API key | Secret |
| BETTER_AUTH_SECRET | JWT signing secret | Secret |
| FRONTEND_URL | CORS allowed origin | ConfigMap |
| PORT | Server port | values.yaml |

## File Structure After Deployment

```
project-root/
├── frontend/
│   ├── Dockerfile          # Multi-stage Next.js build
│   └── .dockerignore
├── backend/
│   ├── Dockerfile          # FastAPI container
│   └── .dockerignore
├── helm/
│   ├── frontend/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   └── backend/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-local.yaml  # GITIGNORED - contains secrets
│       └── templates/
└── .gitignore              # Updated to exclude values-local.yaml
```
