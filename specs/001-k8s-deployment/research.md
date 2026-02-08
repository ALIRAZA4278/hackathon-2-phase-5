# Research: Local Kubernetes Deployment

**Feature**: 001-k8s-deployment
**Date**: 2026-01-23
**Status**: Complete

## Overview

This document captures technology decisions, best practices research, and rationale for the Phase IV Kubernetes deployment implementation.

## Research Topics

### 1. Docker Multi-Stage Builds for Next.js

**Decision**: Use multi-stage build pattern for frontend

**Rationale**:
- Separates build dependencies (node_modules, TypeScript compiler) from runtime
- Final image only contains production build output and minimal runtime
- Significantly reduces image size (from ~1GB to ~200-400MB typically)
- Security: Build tools not present in production image

**Best Practices Adopted**:
- Stage 1 (deps): Install node_modules with npm ci for deterministic builds
- Stage 2 (builder): Build Next.js production output
- Stage 3 (runner): Copy only standalone output, use node:alpine for runtime
- Use `.dockerignore` to exclude .next, node_modules from build context

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Single-stage build | Image too large (~1GB+), includes dev dependencies |
| Docker BuildKit caching only | Still includes build deps in final image |
| External build + COPY | More complex CI/CD, less reproducible |

### 2. Python Docker Image Strategy

**Decision**: Use single-stage build with python:3.11-slim

**Rationale**:
- Python pip install is straightforward without complex build steps
- Slim image already minimal (~150MB base)
- No compilation needed (all dependencies are wheels)
- Multi-stage adds complexity without significant size benefit

**Best Practices Adopted**:
- Use `--no-cache-dir` with pip to avoid caching packages
- Copy requirements.txt first for layer caching
- Non-root user for security (future enhancement)
- Explicit Python version tag

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| python:3.11-alpine | Some packages don't have alpine wheels, compilation needed |
| Multi-stage build | Unnecessary complexity for simple pip install |
| Distroless Python | Less debugging capability, overkill for local deployment |

### 3. Minikube Docker Integration

**Decision**: Use Minikube's built-in Docker daemon for image building

**Rationale**:
- Avoids image pull from external registry
- Images built directly in Minikube's Docker context
- Faster development cycle
- No need for local registry setup

**Implementation**:
```bash
# Point shell to Minikube's Docker
eval $(minikube docker-env)

# Build images (now available to Minikube pods)
docker build -t todo-frontend:1.0.0 ./frontend
docker build -t todo-backend:1.0.0 ./backend
```

**Best Practices**:
- Set `imagePullPolicy: Never` or `IfNotPresent` in Kubernetes deployments
- Use explicit image tags (not `latest`) for reproducibility
- Run `minikube image ls` to verify images are available

### 4. Helm Chart Structure

**Decision**: One chart per service (frontend, backend) with optional umbrella chart

**Rationale**:
- Independent deployment and versioning per service
- Clear separation of concerns
- Each service can be upgraded independently
- Umbrella chart provides single-command full deployment option

**Best Practices Adopted**:
- All configuration via values.yaml
- Use helpers template (`_helpers.tpl`) for common labels/selectors
- Separate Secret template (not actual secret values)
- Resource requests defined for all containers

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Single monolithic chart | Harder to upgrade services independently |
| Kustomize | Helm required by constitution |
| Raw Kubernetes YAML | Not declarative, harder to manage config |

### 5. Kubernetes Service Types

**Decision**:
- Frontend: NodePort (external access via Minikube)
- Backend: ClusterIP (internal only)

**Rationale**:
- NodePort allows Minikube to expose frontend to host browser
- ClusterIP keeps backend internal (frontend → backend communication in-cluster)
- No LoadBalancer needed (Minikube tunnel or NodePort sufficient)

**Implementation**:
- Frontend Service: `type: NodePort`, port 3000
- Backend Service: `type: ClusterIP`, port 8000
- Frontend ConfigMap: `NEXT_PUBLIC_API_URL=http://backend:8000`

### 6. Secrets Management in Kubernetes

**Decision**: Use Kubernetes Secret resources with Helm templating

**Rationale**:
- Secrets stored separately from application config
- Values never committed to Git (use values-local.yaml, gitignored)
- Injected as environment variables at runtime
- Constitution compliant

**Implementation**:
```yaml
# secret.yaml template (no actual values)
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "backend.fullname" . }}
type: Opaque
data:
  DATABASE_URL: {{ .Values.secrets.databaseUrl | b64enc }}
  GEMINI_API_KEY: {{ .Values.secrets.geminiApiKey | b64enc }}
  BETTER_AUTH_SECRET: {{ .Values.secrets.betterAuthSecret | b64enc }}
```

**Best Practices**:
- Never commit actual secret values
- Use `values-local.yaml` for local development (gitignored)
- Consider external secret managers for production (out of scope)

### 7. Health Probes

**Decision**: Implement readiness and liveness probes for both services

**Rationale**:
- Kubernetes can detect unhealthy pods and restart them
- Traffic only routed to ready pods
- Better deployment reliability

**Implementation**:
```yaml
# Backend
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5

# Frontend
livenessProbe:
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 30
  periodSeconds: 10
```

**Note**: Backend may need a `/health` endpoint added (simple 200 OK response)

### 8. Resource Requests and Limits

**Decision**: Define resource requests, limits optional for local deployment

**Rationale**:
- Requests ensure pods get minimum resources
- Limits prevent runaway resource consumption
- Constitution requires requests, recommends limits

**Implementation**:
| Service | CPU Request | Memory Request | CPU Limit | Memory Limit |
|---------|-------------|----------------|-----------|--------------|
| Frontend | 100m | 128Mi | 500m | 512Mi |
| Backend | 100m | 256Mi | 500m | 512Mi |

## Decisions Summary

| # | Decision | Choice | Confidence |
|---|----------|--------|------------|
| 1 | Frontend Docker pattern | Multi-stage | High |
| 2 | Backend Docker pattern | Single-stage slim | High |
| 3 | Minikube image strategy | Direct build via docker-env | High |
| 4 | Helm structure | One chart per service | High |
| 5 | Frontend service type | NodePort | High |
| 6 | Backend service type | ClusterIP | High |
| 7 | Secrets management | K8s Secrets + values-local.yaml | High |
| 8 | Health probes | Both services | Medium |
| 9 | Resource requests | Defined per service | High |

## Open Questions Resolved

All technical questions have been resolved. No NEEDS CLARIFICATION items remain.

## References

- Kubernetes Best Practices: https://kubernetes.io/docs/concepts/configuration/overview/
- Helm Chart Best Practices: https://helm.sh/docs/chart_best_practices/
- Next.js Docker Documentation: https://nextjs.org/docs/pages/building-your-application/deploying#docker-image
- Minikube Handbook: https://minikube.sigs.k8s.io/docs/handbook/
