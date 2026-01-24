# Data Model: Infrastructure Entities

**Feature**: 001-k8s-deployment
**Date**: 2026-01-23
**Status**: Complete

## Overview

This document defines the infrastructure entities (Kubernetes resources, Docker artifacts, Helm components) for the Phase IV deployment. Unlike application data models, these represent infrastructure-as-code objects.

## Docker Entities

### Docker Image: Frontend

| Attribute | Value | Description |
|-----------|-------|-------------|
| Name | todo-frontend | Image repository name |
| Tag | 1.0.0 | Semantic version tag |
| Base Image | node:20-alpine | Runtime base (final stage) |
| Build Base | node:20-alpine | Build stage base |
| Exposed Port | 3000 | Next.js default port |
| Workdir | /app | Application directory |
| User | nextjs | Non-root user |
| Max Size | 500MB | Constitutional limit |

**Build Stages**:
1. `deps` - Install node_modules
2. `builder` - Build Next.js production output
3. `runner` - Final minimal runtime image

### Docker Image: Backend

| Attribute | Value | Description |
|-----------|-------|-------------|
| Name | todo-backend | Image repository name |
| Tag | 1.0.0 | Semantic version tag |
| Base Image | python:3.11-slim | Single-stage base |
| Exposed Port | 8000 | FastAPI port |
| Workdir | /app | Application directory |
| Max Size | 300MB | Constitutional limit |

## Kubernetes Entities

### Namespace (Optional)

| Attribute | Value | Description |
|-----------|-------|-------------|
| Name | default | Using default namespace |
| Labels | app: todo | Application identifier |

### Deployment: Frontend

| Attribute | Value | Configurable Via |
|-----------|-------|------------------|
| Name | todo-frontend | Helm chart name |
| Replicas | 1 | values.yaml: replicaCount |
| Image | todo-frontend:1.0.0 | values.yaml: image.repository, image.tag |
| Image Pull Policy | IfNotPresent | values.yaml: image.pullPolicy |
| Container Port | 3000 | values.yaml: service.targetPort |
| CPU Request | 100m | values.yaml: resources.requests.cpu |
| Memory Request | 128Mi | values.yaml: resources.requests.memory |
| CPU Limit | 500m | values.yaml: resources.limits.cpu |
| Memory Limit | 512Mi | values.yaml: resources.limits.memory |
| Restart Policy | Always | Kubernetes default |
| Strategy | RollingUpdate | Helm template |

**Environment Variables**:
| Variable | Source | Description |
|----------|--------|-------------|
| NEXT_PUBLIC_API_URL | ConfigMap | Backend service URL |
| NODE_ENV | values.yaml | production |

**Probes**:
| Type | Path | Port | Initial Delay | Period |
|------|------|------|---------------|--------|
| Liveness | / | 3000 | 30s | 10s |
| Readiness | / | 3000 | 5s | 5s |

### Deployment: Backend

| Attribute | Value | Configurable Via |
|-----------|-------|------------------|
| Name | todo-backend | Helm chart name |
| Replicas | 1 | values.yaml: replicaCount |
| Image | todo-backend:1.0.0 | values.yaml: image.repository, image.tag |
| Image Pull Policy | IfNotPresent | values.yaml: image.pullPolicy |
| Container Port | 8000 | values.yaml: service.targetPort |
| CPU Request | 100m | values.yaml: resources.requests.cpu |
| Memory Request | 256Mi | values.yaml: resources.requests.memory |
| CPU Limit | 500m | values.yaml: resources.limits.cpu |
| Memory Limit | 512Mi | values.yaml: resources.limits.memory |
| Restart Policy | Always | Kubernetes default |
| Strategy | RollingUpdate | Helm template |

**Environment Variables**:
| Variable | Source | Description |
|----------|--------|-------------|
| DATABASE_URL | Secret | Neon PostgreSQL connection |
| GEMINI_API_KEY | Secret | AI API key |
| BETTER_AUTH_SECRET | Secret | JWT signing key |
| FRONTEND_URL | ConfigMap | CORS allowed origin |
| PORT | values.yaml | 8000 |

**Probes**:
| Type | Path | Port | Initial Delay | Period |
|------|------|------|---------------|--------|
| Liveness | /health | 8000 | 10s | 10s |
| Readiness | /health | 8000 | 5s | 5s |

### Service: Frontend

| Attribute | Value | Description |
|-----------|-------|-------------|
| Name | todo-frontend | Service name |
| Type | NodePort | External access via Minikube |
| Port | 3000 | Service port |
| Target Port | 3000 | Container port |
| Node Port | Auto-assigned | Minikube accessible port |
| Selector | app: todo-frontend | Pod selector |

### Service: Backend

| Attribute | Value | Description |
|-----------|-------|-------------|
| Name | todo-backend | Service name |
| Type | ClusterIP | Internal cluster access |
| Port | 8000 | Service port |
| Target Port | 8000 | Container port |
| Selector | app: todo-backend | Pod selector |

### ConfigMap: Frontend

| Key | Value | Description |
|-----|-------|-------------|
| NEXT_PUBLIC_API_URL | http://todo-backend:8000 | Backend service URL |

### ConfigMap: Backend

| Key | Value | Description |
|-----|-------|-------------|
| FRONTEND_URL | http://todo-frontend:3000 | CORS allowed origin |

### Secret: Backend

| Key | Source | Description |
|-----|--------|-------------|
| DATABASE_URL | values-local.yaml | Neon PostgreSQL URL |
| GEMINI_API_KEY | values-local.yaml | Gemini AI API key |
| BETTER_AUTH_SECRET | values-local.yaml | JWT secret |

**Note**: Actual secret values stored in `values-local.yaml` (gitignored), referenced via Helm template.

## Helm Entities

### Chart: Frontend

| Attribute | Value |
|-----------|-------|
| Name | todo-frontend |
| Version | 1.0.0 |
| App Version | 1.0.0 |
| API Version | v2 |
| Type | application |

**Templates**:
- `deployment.yaml` - Kubernetes Deployment
- `service.yaml` - Kubernetes Service
- `configmap.yaml` - Environment ConfigMap
- `_helpers.tpl` - Template helpers

### Chart: Backend

| Attribute | Value |
|-----------|-------|
| Name | todo-backend |
| Version | 1.0.0 |
| App Version | 1.0.0 |
| API Version | v2 |
| Type | application |

**Templates**:
- `deployment.yaml` - Kubernetes Deployment
- `service.yaml` - Kubernetes Service
- `configmap.yaml` - Environment ConfigMap
- `secret.yaml` - Secret template
- `_helpers.tpl` - Template helpers

## Entity Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                     Minikube Cluster                         │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                  Default Namespace                   │    │
│  │                                                      │    │
│  │  ┌─────────────────┐      ┌─────────────────┐       │    │
│  │  │ Deployment      │      │ Deployment      │       │    │
│  │  │ todo-frontend   │      │ todo-backend    │       │    │
│  │  │ (1-3 replicas)  │      │ (1-3 replicas)  │       │    │
│  │  └────────┬────────┘      └────────┬────────┘       │    │
│  │           │                        │                 │    │
│  │  ┌────────▼────────┐      ┌────────▼────────┐       │    │
│  │  │ Service         │      │ Service         │       │    │
│  │  │ NodePort:3000   │─────▶│ ClusterIP:8000  │       │    │
│  │  └─────────────────┘      └────────┬────────┘       │    │
│  │                                    │                 │    │
│  │  ┌─────────────────┐      ┌────────▼────────┐       │    │
│  │  │ ConfigMap       │      │ Secret          │       │    │
│  │  │ (API URL)       │      │ (DB, API keys)  │       │    │
│  │  └─────────────────┘      └─────────────────┘       │    │
│  │                                                      │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               │ External Connection
                               ▼
                    ┌─────────────────────┐
                    │ Neon PostgreSQL     │
                    │ (Cloud Database)    │
                    └─────────────────────┘
```

## Validation Rules

| Entity | Rule | Enforcement |
|--------|------|-------------|
| Docker Image | Must have explicit tag | Helm values validation |
| Docker Image | Must not exceed size limit | Manual build validation |
| Deployment | Must have resource requests | Helm template |
| Deployment | Must have health probes | Helm template |
| Service | Must have correct type | Helm values |
| Secret | Must not contain values in Git | .gitignore |
| ConfigMap | Must not contain secrets | Code review |
