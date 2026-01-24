# Implementation Plan: Local Kubernetes Deployment

**Branch**: `001-k8s-deployment` | **Date**: 2026-01-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-k8s-deployment/spec.md`

## Summary

Deploy the existing Phase III Todo AI Chatbot application to a local Kubernetes cluster using Minikube. This involves containerizing both frontend (Next.js) and backend (FastAPI) services using Docker with AI-assisted Dockerfile generation (Gordon), creating Helm charts for declarative deployment, and establishing AI-assisted operational workflows using kubectl-ai and Kagent.

## Technical Context

**Infrastructure Stack**:
- Container Runtime: Docker Desktop (with Gordon AI Agent)
- Orchestration: Kubernetes via Minikube
- Package Manager: Helm 3.x
- AI DevOps: kubectl-ai, Kagent

**Application Stack** (existing from Phase III):
- Frontend: Next.js 15+ / TypeScript / Tailwind CSS / Better Auth
- Backend: Python 3.11 / FastAPI / SQLModel / OpenAI SDK
- Database: Neon Serverless PostgreSQL (external, unchanged)
- Authentication: Better Auth / JWT

**Testing**: Manual validation via kubectl, helm, and Minikube service access
**Target Platform**: Local Minikube cluster on Windows/Mac/Linux
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Pods running within 2 minutes, images under 500MB (frontend) / 300MB (backend)
**Constraints**: No cloud deployments, no application code changes, Minikube default configuration only
**Scale/Scope**: Single-node local cluster, 1-3 replicas per service

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Everything is Containerized | ✅ PASS | Frontend and backend will have dedicated Dockerfiles |
| II. Stateless by Design | ✅ PASS | Application already stateless; all state in Neon PostgreSQL |
| III. Declarative Infrastructure | ✅ PASS | Helm charts as single deployment authority |
| IV. Reproducibility | ✅ PASS | Complete deployment via documented Helm commands |
| V. AI-Assisted Operations First | ✅ PASS | Gordon, kubectl-ai, Kagent used throughout |
| Docker Constitution | ✅ PASS | Multi-stage builds, explicit tags, no secrets in images |
| Kubernetes Constitution | ✅ PASS | Deployment + Service per component, configurable replicas |
| Helm Chart Constitution | ✅ PASS | One chart per service, values.yaml controls all config |
| Security Rules | ✅ PASS | Secrets in K8s Secret resources, not in Git or images |

**Gate Result**: ✅ PASS - No constitutional violations detected

## Project Structure

### Documentation (this feature)

```text
specs/001-k8s-deployment/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0: Technology decisions
├── data-model.md        # Phase 1: Infrastructure entities
├── quickstart.md        # Phase 1: Deployment guide
├── contracts/           # Phase 1: Helm value schemas
│   ├── frontend-values.yaml
│   └── backend-values.yaml
├── checklists/
│   └── requirements.md  # Quality validation checklist
└── tasks.md             # Phase 2: Implementation tasks
```

### Infrastructure Code (repository root)

```text
# Docker files
frontend/
├── Dockerfile           # NEW: Multi-stage Next.js build
└── .dockerignore        # NEW: Exclude node_modules, .next, etc.

backend/
├── Dockerfile           # UPDATE: Modify for Minikube (port 8000)
└── .dockerignore        # NEW: Exclude .venv, __pycache__, etc.

# Helm charts
helm/
├── frontend/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── deployment.yaml
│       ├── service.yaml
│       └── configmap.yaml
├── backend/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── secret.yaml
│       └── configmap.yaml
└── todo-app/            # Optional umbrella chart
    ├── Chart.yaml
    └── values.yaml

# Git security
.gitignore               # UPDATE: Add helm/**/values-local.yaml
```

**Structure Decision**: Web application structure with separate `frontend/` and `backend/` directories (already exists). New `helm/` directory at repository root for Kubernetes packaging.

## Execution Phases

### Phase 4.1: Environment Validation & Cluster Readiness

**Objective**: Verify all tools are installed and Minikube cluster is operational.

**Steps**:
1. Verify Docker Desktop is running with Gordon AI Agent enabled
2. Start Minikube cluster with Docker driver
3. Confirm kubectl context is set to Minikube
4. Verify Helm, kubectl-ai, and Kagent availability
5. Run initial cluster health check with Kagent

**AI Tool Usage**:
- Gordon: Verify Docker environment readiness
- kubectl-ai: Inspect cluster nodes and namespaces
- Kagent: Initial cluster health scan

**Validation Checkpoint**:
- [ ] `minikube status` shows Running
- [ ] `kubectl get nodes` shows Ready
- [ ] `helm version` returns Helm 3.x
- [ ] Docker can build images
- [ ] No critical cluster health issues

### Phase 4.2: AI-Assisted Containerization

**Objective**: Generate optimized Dockerfiles for frontend and backend using Gordon.

**Steps**:
1. Use Gordon to analyze frontend (Next.js) and generate Dockerfile
2. Use Gordon to analyze/optimize backend (FastAPI) Dockerfile
3. Create .dockerignore files for both services
4. Validate Dockerfiles follow constitution rules

**Decisions Documented**:

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Frontend build pattern | Multi-stage | Separate build deps from runtime, reduce image size |
| Frontend base image | node:20-alpine | Explicit tag, minimal size |
| Backend build pattern | Single-stage | Python deps simpler, slim image sufficient |
| Backend base image | python:3.11-slim | Match existing, explicit tag |
| Backend port | 8000 | Standard FastAPI port (update from 7860) |
| Frontend port | 3000 | Standard Next.js port |

**Validation Checkpoint**:
- [ ] Dockerfiles use explicit base image tags (no `latest`)
- [ ] Multi-stage build used for frontend
- [ ] No secrets or credentials in Dockerfiles
- [ ] .dockerignore excludes build artifacts and dependencies

### Phase 4.3: Image Build & Minikube Integration

**Objective**: Build Docker images and make them available to Minikube.

**Steps**:
1. Configure shell to use Minikube's Docker daemon
2. Build frontend image with Gordon assistance
3. Build backend image with Gordon assistance
4. Tag images consistently for Helm charts
5. Verify images are accessible to Minikube

**Image Naming Convention**:
- Frontend: `todo-frontend:1.0.0`
- Backend: `todo-backend:1.0.0`

**AI Tool Usage**:
- Gordon: Build optimization, error resolution, layer analysis
- kubectl-ai: Verify image availability in cluster context

**Validation Checkpoint**:
- [ ] Frontend image builds successfully
- [ ] Backend image builds successfully
- [ ] Frontend image < 500MB
- [ ] Backend image < 300MB
- [ ] Images visible to Minikube (`minikube image ls`)

### Phase 4.4: Helm Chart Generation

**Objective**: Create Helm charts for declarative Kubernetes deployment.

**Steps**:
1. Create `helm/` directory structure
2. Generate frontend Helm chart with Deployment, Service, ConfigMap
3. Generate backend Helm chart with Deployment, Service, Secret, ConfigMap
4. Define values.yaml with all configurable parameters
5. Lint charts with `helm lint`

**Chart Structure** (per Constitution):
```
helm/
├── frontend/
│   ├── Chart.yaml           # name, version, appVersion
│   ├── values.yaml          # image, replicas, service, env
│   └── templates/
│       ├── _helpers.tpl     # Template helpers
│       ├── deployment.yaml  # Pod spec with probes
│       ├── service.yaml     # NodePort for external access
│       └── configmap.yaml   # NEXT_PUBLIC_API_URL
├── backend/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── _helpers.tpl
│       ├── deployment.yaml  # Pod spec with probes
│       ├── service.yaml     # ClusterIP for internal access
│       ├── secret.yaml      # Template for secrets
│       └── configmap.yaml   # Non-sensitive config
```

**Values.yaml Parameters** (per Constitution):

| Parameter | Frontend | Backend |
|-----------|----------|---------|
| image.repository | todo-frontend | todo-backend |
| image.tag | 1.0.0 | 1.0.0 |
| replicaCount | 1 | 1 |
| service.type | NodePort | ClusterIP |
| service.port | 3000 | 8000 |
| resources.requests.cpu | 100m | 100m |
| resources.requests.memory | 128Mi | 256Mi |
| env.* | NEXT_PUBLIC_API_URL | DATABASE_URL, etc. |

**Validation Checkpoint**:
- [ ] `helm lint helm/frontend` passes
- [ ] `helm lint helm/backend` passes
- [ ] values.yaml controls all configurable parameters
- [ ] No hard-coded values in templates

### Phase 4.5: Kubernetes Deployment via Helm

**Objective**: Deploy application to Minikube using Helm charts.

**Steps**:
1. Create Kubernetes namespace (optional: `todo`)
2. Create backend Secret resource with actual values
3. Install backend Helm chart
4. Install frontend Helm chart
5. Verify pods reach Running state
6. Expose frontend via Minikube service

**Deployment Order**:
1. Backend first (frontend depends on API)
2. Frontend second (needs backend service URL)

**AI Tool Usage**:
- kubectl-ai: Deploy and monitor rollout
- Kagent: Analyze pod behavior during startup

**Validation Checkpoint**:
- [ ] `kubectl get pods` shows all Running
- [ ] `kubectl get services` shows correct ports
- [ ] `minikube service frontend --url` returns accessible URL
- [ ] Frontend loads in browser
- [ ] AI chatbot responds to messages

### Phase 4.6: AI-Assisted Operations & Optimization

**Objective**: Demonstrate AI-assisted cluster management capabilities.

**Operational Scenarios**:

| Scenario | AI Tool | Command/Intent |
|----------|---------|----------------|
| Scale frontend | kubectl-ai | "scale frontend deployment to 3 replicas" |
| Check pod logs | kubectl-ai | "show logs for backend pod" |
| Debug failure | kubectl-ai | "why is backend pod failing" |
| Cluster health | Kagent | "analyze cluster health" |
| Resource usage | Kagent | "show resource utilization" |

**Validation Checkpoint**:
- [ ] kubectl-ai responds to natural language queries
- [ ] Scaling works without downtime
- [ ] Kagent provides actionable insights

### Phase 4.7: Validation, Failure Simulation & Quality Assurance

**Objective**: Validate all success criteria from specification.

**Validation Tests**:

| Test | Command | Expected Result |
|------|---------|-----------------|
| Pod restart survival | `kubectl delete pod <backend-pod>` | New pod starts, tasks persist |
| Scaling | `kubectl scale deployment frontend --replicas=3` | 3 pods running, app accessible |
| Helm upgrade | `helm upgrade frontend ./helm/frontend --set replicaCount=2` | Deployment updates |
| Helm rollback | `helm rollback frontend 1` | Returns to previous config |
| Fresh deployment | Delete all, reinstall | Works without manual fixes |

**Quality Gates**:
- [ ] SC-001: Deploy via helm install within 5 minutes
- [ ] SC-002: Pods reach Running within 2 minutes
- [ ] SC-003: App accessible, chatbot responds
- [ ] SC-004: Survives pod deletion, zero data loss
- [ ] SC-005: Scaling completes within 1 minute
- [ ] SC-006: Fresh deployment succeeds
- [ ] SC-007: No secrets in Git or images
- [ ] SC-008: Helm upgrade/rollback works

## Complexity Tracking

> **No constitutional violations detected. This section remains empty.**

## Artifacts Generated

| Phase | Artifact | Location |
|-------|----------|----------|
| 4.2 | Frontend Dockerfile | frontend/Dockerfile |
| 4.2 | Frontend .dockerignore | frontend/.dockerignore |
| 4.2 | Backend Dockerfile | backend/Dockerfile (updated) |
| 4.2 | Backend .dockerignore | backend/.dockerignore |
| 4.3 | Docker images | Minikube local registry |
| 4.4 | Frontend Helm chart | helm/frontend/ |
| 4.4 | Backend Helm chart | helm/backend/ |
| 4.5 | Running Kubernetes deployment | Minikube cluster |

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Minikube resource constraints | Medium | High | Use Kagent to monitor, adjust resource requests |
| Image pull failures | Low | Medium | Use Minikube Docker daemon directly |
| Secret misconfiguration | Medium | High | Template validation, dry-run installs |
| Port conflicts | Low | Low | Use NodePort with explicit ports |
| Network connectivity to Neon DB | Medium | High | Verify connectivity before deployment |

## Next Steps After Plan Approval

1. Run `/sp.tasks` to generate implementation task list
2. Execute Phase 4.1 (Environment Validation)
3. Proceed through phases sequentially
4. Create PHR after each significant milestone
