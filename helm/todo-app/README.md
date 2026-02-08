# Todo App Umbrella Helm Chart

This is the umbrella Helm chart for the Phase V Cloud-Native AI Todo Platform. It orchestrates the deployment of the entire application stack including backend, frontend, consumer services, and infrastructure components.

## Architecture

The application consists of:

- **Application Services**: Backend API (FastAPI), Frontend (Next.js)
- **Consumer Services**: Reminder, Recurring, Audit, Notification consumers
- **Infrastructure**: Redpanda (Kafka), Redis, Observability (Prometheus + Grafana)
- **Service Mesh**: Dapr sidecars for all application components

## Prerequisites

1. Kubernetes cluster (v1.24+)
2. Helm 3.x installed
3. Dapr installed in the cluster
4. PostgreSQL database (Neon) accessible from the cluster

## Installation

### 1. Update Dependencies

First, update the chart dependencies:

```bash
cd helm/todo-app
helm dependency update
```

### 2. Configure Secrets

Create a `values-local.yaml` file (this file is gitignored):

```yaml
backend:
  secrets:
    databaseUrl: "postgresql://user:pass@host.neon.tech:5432/dbname?sslmode=require"
    geminiApiKey: "your-gemini-api-key"
    betterAuthSecret: "your-better-auth-secret"
```

### 3. Install the Chart

```bash
helm install todo-app . -f values-local.yaml
```

Or upgrade an existing release:

```bash
helm upgrade todo-app . -f values-local.yaml
```

## Configuration

### Enabling/Disabling Components

You can selectively enable or disable components in `values.yaml`:

```yaml
backend:
  enabled: true  # Set to false to disable backend

frontend:
  enabled: true

reminder:
  enabled: true

# Infrastructure components
redpanda:
  enabled: true  # Set to false if using external Kafka

observability:
  enabled: true  # Set to false to skip monitoring
```

### Resource Configuration

Adjust resource limits for each component:

```yaml
backend:
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi
```

### Image Configuration

Override image repositories and tags:

```yaml
backend:
  image:
    repository: your-registry/todo-backend
    tag: "v2.0.0"
    pullPolicy: Always
```

## Accessing the Application

### Frontend

After installation, get the frontend URL:

```bash
export NODE_PORT=$(kubectl get svc todo-app-frontend -o jsonpath='{.spec.ports[0].nodePort}')
export NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[0].address}')
echo "http://$NODE_IP:$NODE_PORT"
```

### Backend API

Port-forward to access the API:

```bash
kubectl port-forward svc/todo-app-backend 8000:8000
```

Then visit: http://localhost:8000/docs

### Grafana Dashboard

Access Grafana via NodePort:

```bash
# Default port is 32000
echo "http://<NODE_IP>:32000"

# Default credentials:
# Username: admin
# Password: admin
```

## Monitoring

### Prometheus

Port-forward to access Prometheus:

```bash
kubectl port-forward svc/todo-app-observability-prometheus 9090:9090
```

Visit: http://localhost:9090

### Checking Deployment Status

```bash
# Check all pods
kubectl get pods

# Check Dapr sidecars
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}'

# View logs
kubectl logs -l app=todo-backend -f
kubectl logs -l app=reminder-consumer -f
```

## Troubleshooting

### Pods Not Starting

Check pod status and events:

```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### Dapr Issues

Verify Dapr is installed:

```bash
kubectl get pods -n dapr-system
```

Check Dapr sidecar injection:

```bash
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[*].name}'
# Should see both app container and daprd sidecar
```

### Database Connection Issues

Verify database URL is correctly configured:

```bash
kubectl get secret todo-app-backend-secret -o jsonpath='{.data.DATABASE_URL}' | base64 -d
```

## Uninstallation

```bash
helm uninstall todo-app
```

## Chart Structure

```
todo-app/
├── Chart.yaml              # Chart metadata and dependencies
├── values.yaml             # Default configuration values
├── templates/
│   ├── _helpers.tpl        # Template helpers
│   └── NOTES.txt          # Post-install instructions
└── charts/                 # Sub-chart dependencies (auto-generated)
```

## Sub-Charts

This umbrella chart includes:

- `backend` (todo-backend)
- `frontend` (todo-frontend)
- `reminder` (reminder-consumer)
- `recurring` (recurring-consumer)
- `audit` (audit-consumer)
- `notification` (notification-consumer)
- `redpanda`
- `redis`
- `observability`

Each sub-chart can be configured independently via the umbrella chart's `values.yaml`.

## Production Considerations

1. **Secrets Management**: Use external secret managers (e.g., External Secrets Operator)
2. **Persistence**: Configure proper storage classes for Redpanda persistence
3. **Resource Limits**: Adjust based on load testing results
4. **Monitoring**: Set up Grafana dashboards and alerts
5. **High Availability**: Increase replica counts for critical services
6. **Network Policies**: Implement network policies for security
7. **TLS**: Enable TLS for all service-to-service communication

## License

MIT
