<!--
================================================================================
SYNC IMPACT REPORT
================================================================================
Version Change: 2.0.0 → 3.0.0 (MAJOR - Phase IV Kubernetes Deployment System)

Modified Principles:
  - System Mission → Extended with Cloud-Native Deployment Objective
  - Principle VIII "Technology Stack Compliance" → Extended with K8s/Docker/Helm stack
  - Principle X "Quality Assurance" → Extended with deployment validation rules

Added Sections:
  - Phase IV Purpose & Intent
  - Phase IV Scope Boundaries
  - Infrastructure Principles (NON-NEGOTIABLE)
  - Docker Constitution
  - Kubernetes Constitution
  - Helm Chart Constitution
  - Security & Configuration Rules (Extended)
  - AI DevOps Governance (Gordon, kubectl-ai, Kagent)
  - Phase IV Validation & Success Criteria
  - Phase IV Failure Conditions (Hard Stops)
  - Relationship to Previous Phases

Removed Sections:
  - None (Phase III sections retained for context)

Templates Requiring Updates:
  ✅ plan-template.md - Constitution Check section compatible with K8s deployment
  ✅ spec-template.md - Requirements section aligns with infra-as-code specs
  ✅ tasks-template.md - Phase structure supports Docker/K8s/Helm tasks

Follow-up TODOs: None

================================================================================
-->

# Hackathon Todo – Phase IV Constitution

**Phase Name**: Local Kubernetes Deployment of Cloud-Native Todo AI Chatbot
**Development Model**: Spec-Driven, Agentic Dev Stack
**Implementation Tooling**: Claude Code + Spec-Kit Plus + AI DevOps Agents

This constitution serves as the single source of truth for how the system is containerized, deployed, and operated. All plans, tasks, implementations, and evaluations MUST comply with this document.

## System Mission

Deploy the completed Phase III Todo AI Chatbot as a fully containerized, cloud-native system on a local Kubernetes cluster using Minikube.

This phase evaluates:
- Cloud-native thinking
- Infrastructure automation discipline
- Stateless architecture correctness
- AI-assisted DevOps usage
- Production-grade deployment practices

**This phase is NOT about adding new application features. It is about operational excellence.**

The system MUST be built using the Agentic Dev Stack workflow with NO manual coding, relying strictly on Spec-Kit Plus, Claude Code, and AI DevOps agents.

## Phase IV Purpose & Intent

Phase IV exists to transform the completed Phase III Todo AI Chatbot into a fully containerized, cloud-native system deployed on a local Kubernetes cluster using Minikube.

**Goals:**
- Demonstrate cloud-native deployment competency
- Validate stateless architecture design
- Showcase AI-assisted DevOps workflows
- Produce a reproducible, production-credible deployment

## Phase IV Scope Boundaries

### In Scope (Phase IV)

- Docker containerization of frontend and backend
- Kubernetes deployment using Minikube
- Helm charts for application packaging
- AI-assisted DevOps using Docker AI Agent (Gordon), kubectl-ai, and Kagent
- Secure configuration using environment variables
- Stateless deployment validation
- Service exposure via Minikube

### Out of Scope (Phase IV)

- New application logic
- New AI behaviors or MCP tools
- Cloud provider deployments (AWS/GCP/Azure)
- Manual infrastructure configuration outside specs
- Database deployment (Neon PostgreSQL remains external)
- CI/CD pipelines
- Ingress controllers or load balancers beyond Minikube defaults

## Authoritative Stack (Phase IV)

The only allowed tools and technologies for Phase IV are:

| Tool | Purpose | Status |
|------|---------|--------|
| Docker Desktop | Container runtime | Required |
| Docker AI Agent (Gordon) | Image creation/optimization | Preferred |
| Minikube | Local Kubernetes cluster | Required |
| Helm | Kubernetes package manager | Required |
| kubectl-ai | AI-assisted kubectl operations | Preferred |
| Kagent | Advanced AI Ops agent | Optional |
| Claude Code + Spec-Kit Plus | Development workflow | Required |

Manual shell scripting, ad-hoc YAML editing, or undocumented steps are FORBIDDEN unless explicitly authorized in specs.

## Infrastructure Principles (NON-NEGOTIABLE)

### I. Everything is Containerized

Frontend and backend MUST run only inside containers. No local execution assumptions.

**Rules:**
- Each service MUST have its own Dockerfile
- Images MUST be minimal and use explicit base images
- Containers MUST expose only required ports
- No application code MUST run directly on host machine during deployment

### II. Stateless by Design

Pods MUST hold no state. All state lives in Neon PostgreSQL or external services.

**Rules:**
- Server MUST NOT store any data in container filesystem
- All conversation history MUST be loaded from external database per request
- System MUST survive pod restarts without data loss
- No PersistentVolumeClaims for application data

### III. Declarative Infrastructure

Kubernetes resources MUST be defined declaratively. Helm charts are the single deployment authority.

**Rules:**
- All Kubernetes resources MUST be defined in YAML/Helm templates
- No imperative `kubectl create` or `kubectl run` commands for deployment
- Helm charts MUST be the single source of truth for deployment configuration
- Values.yaml MUST control all configurable parameters

### IV. Reproducibility

Any machine with Minikube MUST be able to reproduce the deployment. No hidden steps or manual tweaks.

**Rules:**
- Complete deployment MUST be achievable via documented Helm commands
- No manual post-deployment fixes allowed
- All dependencies MUST be explicitly declared
- Environment setup MUST be documented and scriptable

### V. AI-Assisted Operations First

Prefer Gordon, kubectl-ai, and Kagent for DevOps actions. Human-written commands are fallback only.

**Rules:**
- Docker AI (Gordon) MUST be used for Dockerfile generation and optimization when available
- kubectl-ai MUST be preferred for deployment, scaling, and debugging operations
- Kagent SHOULD be used for cluster health analysis
- Manual commands MUST be justified when AI tools are bypassed

## Docker Constitution

### Dockerfile Requirements

Each service (frontend, backend) MUST have its own Dockerfile following these rules:

**Image Design:**
- Use explicit base image tags (no `latest`)
- Use multi-stage builds to minimize final image size
- Expose only the required port (3000 for frontend, 8000 for backend)
- Set appropriate user (non-root where possible)

**Security:**
- Secrets MUST NOT be baked into images
- No sensitive data in build args
- No credentials in Dockerfile comments or labels

**Build Context:**
- Include appropriate .dockerignore
- Minimize build context size
- Cache layers effectively

**Docker AI (Gordon) Usage:**
- MUST be used for initial Dockerfile generation when available
- MUST be used for Dockerfile optimization suggestions
- MUST be used for explaining Docker build behavior

### Container Runtime

- Containers MUST work with Docker Desktop on Windows/Mac/Linux
- Containers MUST be compatible with Minikube's Docker daemon
- Environment variables MUST be injectable at runtime

## Kubernetes Constitution

### Cluster Requirements

- Minikube is the ONLY allowed cluster for Phase IV
- Cluster MUST be startable with default settings
- No custom Minikube addons required (except those explicitly documented)

### Resource Requirements

Each application component MUST have:

| Resource | Frontend | Backend |
|----------|----------|---------|
| Deployment | Required | Required |
| Service | Required | Required |
| ConfigMap | As needed | As needed |
| Secret | Not for frontend | Required |

### Deployment Specifications

**Replicas:**
- MUST be configurable via Helm values
- Default: 1 replica per service
- MUST support scaling without breaking functionality

**Pod Specifications:**
- MUST be restart-safe (RestartPolicy: Always)
- SHOULD have readiness probes
- SHOULD have liveness probes
- MUST have resource requests defined

**Service Specifications:**
- Frontend: NodePort or LoadBalancer (Minikube tunnel)
- Backend: ClusterIP (internal only) or NodePort
- Port mappings MUST be explicit

### kubectl-ai Governance

kubectl-ai is a first-class operational interface:

- MUST be used for natural-language cluster queries
- MUST be used for deployment troubleshooting
- MUST be used for scaling operations
- MAY be used for resource creation (with review)

### Kagent Governance

Kagent is for cluster analysis and optimization:

- SHOULD be used for cluster health checks
- SHOULD be used for optimization suggestions
- MUST NOT bypass Kubernetes security boundaries

## Helm Chart Constitution

### Chart Structure

One chart per service is MANDATORY:

```
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
└── todo-app/           # Optional umbrella chart
    ├── Chart.yaml
    └── values.yaml
```

### Values.yaml Requirements

Values.yaml MUST control:

| Parameter | Description | Required |
|-----------|-------------|----------|
| image.repository | Docker image name | Yes |
| image.tag | Docker image tag | Yes |
| replicaCount | Number of pod replicas | Yes |
| service.type | Kubernetes service type | Yes |
| service.port | Service port | Yes |
| env.* | Environment variables | Yes |
| resources.requests | CPU/Memory requests | Yes |
| resources.limits | CPU/Memory limits | Recommended |

**No hard-coded values inside templates.** All configuration MUST flow through values.yaml.

### Chart Metadata

Chart.yaml MUST include:
- name: Service identifier
- version: Chart version (semver)
- appVersion: Application version
- description: Brief chart description

## Security & Configuration Rules

### Secrets Management

Secrets (JWT secret, Gemini API key, Database URL) MUST be:
- Stored as Kubernetes Secrets (not plain ConfigMaps)
- Injected as environment variables
- NEVER committed to Git
- NEVER exposed to frontend bundles

**Required Secrets:**
| Secret | Used By | Injected As |
|--------|---------|-------------|
| BETTER_AUTH_SECRET | Backend | Env var |
| DATABASE_URL | Backend | Env var |
| GEMINI_API_KEY | Backend | Env var |

### Environment Variables

| Variable | Service | Source |
|----------|---------|--------|
| BETTER_AUTH_SECRET | Backend | Secret |
| DATABASE_URL | Backend | Secret |
| GEMINI_API_KEY | Backend | Secret |
| NEXT_PUBLIC_API_URL | Frontend | ConfigMap |
| PORT | Both | values.yaml |

### Git Security

- .gitignore MUST exclude all secrets
- values.yaml MUST NOT contain actual secret values
- Use values-local.yaml (gitignored) for local overrides

## AI DevOps Governance

### Docker AI (Gordon)

**Responsibilities:**
- Image creation and Dockerfile optimization
- Explaining Docker build/run behavior
- Suggesting image size reductions
- Debugging container issues

**Constraints:**
- MUST NOT bypass Docker security boundaries
- MUST NOT embed secrets in images
- MUST NOT create privileged containers without justification

### kubectl-ai

**Responsibilities:**
- Deployment, scaling, debugging via natural language
- Cluster state queries
- Resource inspection and troubleshooting

**Constraints:**
- MUST NOT delete production resources without confirmation
- MUST NOT modify system namespaces
- MUST NOT bypass RBAC when configured

### Kagent

**Responsibilities:**
- Cluster health analysis
- Resource optimization suggestions
- Deployment verification

**Constraints:**
- Read-only analysis preferred
- MUST NOT make changes without explicit approval
- MUST NOT access secrets unless necessary

## Core Principles (Inherited from Phase II/III)

### I. Spec-Driven Development (NON-NEGOTIABLE)

All development MUST follow the Agentic Development Stack workflow:

1. Write or update specifications
2. Generate a technical plan from specs
3. Break the plan into tasks
4. Delegate implementation to Claude Code
5. Review outputs and iterate by updating specs

**Rules:**
- Claude Code MUST NEVER implement features not explicitly defined in specs
- Specifications ALWAYS override assumptions
- If a requirement is not written in a spec, it MUST NOT be implemented

### II. Zero Manual Coding

The developer's role is specification authorship, not code authorship.

**Rules:**
- All Dockerfiles, Helm charts, and Kubernetes manifests MUST be written by Claude Code
- Manual edits are forbidden
- Developer interaction is limited to: writing specs, reviewing outputs, approving deployments
- Any code written outside Claude Code violates this constitution

### III. Authentication-First Security

Every API interaction MUST be authenticated and authorized.

**Rules:**
- All API endpoints MUST require a valid JWT token
- JWT MUST be sent in the Authorization header
- Backend MUST decode JWT to extract user identity
- Kubernetes MUST NOT bypass authentication requirements

### IV. User Data Isolation (NON-NEGOTIABLE)

No user may access another user's data under any circumstance.

**Rules:**
- Backend MUST extract user_id from the JWT token
- Every database query MUST filter by authenticated user_id
- Deployment MUST NOT change user isolation behavior

### V. Technology Stack Compliance (Extended)

The technology stack is fixed and non-negotiable.

**Application Stack (from Phase III):**
- Frontend: Next.js 16+ / TypeScript / Tailwind CSS / Better Auth
- Backend: Python FastAPI / SQLModel / OpenAI Agents SDK
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth / JWT

**Infrastructure Stack (Phase IV):**
- Container Runtime: Docker Desktop
- Orchestration: Kubernetes via Minikube
- Packaging: Helm charts
- AI DevOps: Gordon, kubectl-ai, Kagent

## Phase IV Validation & Success Criteria

Phase IV is considered successful ONLY if:

| Criterion | Validation Method |
|-----------|-------------------|
| Frontend runs in Minikube | `kubectl get pods` shows Running |
| Backend runs in Minikube | `kubectl get pods` shows Running |
| Pods survive restarts | `kubectl delete pod` + verify recovery |
| Helm install works | `helm install` completes without errors |
| Helm upgrade works | `helm upgrade` completes without errors |
| Scaling works | `kubectl scale` + functionality test |
| Application accessible | `minikube service` opens working app |
| No local dependencies | Fresh Minikube deployment succeeds |
| Secrets not exposed | No secrets in Git or image layers |

## Phase IV Failure Conditions (Hard Stops)

Execution MUST STOP if:

| Violation | Severity |
|-----------|----------|
| Application runs outside Kubernetes | CRITICAL |
| Secrets are hard-coded | CRITICAL |
| State is stored in pods | CRITICAL |
| Helm is bypassed for deployment | HIGH |
| Manual fixes required after deployment | HIGH |
| AI DevOps tools ignored without justification | MEDIUM |
| Images use `latest` tag | MEDIUM |
| No resource requests defined | LOW |

## Relationship to Previous Phases

### Phase IV MUST:

- Deploy the Phase III system as-is
- Preserve all authentication, AI, and MCP behavior
- NOT modify application logic
- NOT add new features

### Phase IV does NOT replace:

- Phase I (Backend Foundation)
- Phase II (Full-Stack Integration)
- Phase III (AI Chatbot System)

**Phase IV operationalizes Phases I-III.**

## Governance

### Amendment Process

1. Proposed amendments MUST be documented in a spec
2. Amendments MUST include rationale and impact analysis
3. Constitution version MUST be incremented per semantic versioning
4. All dependent artifacts MUST be updated for consistency

### Versioning Policy

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Backward-incompatible principle removal/redefinition | MAJOR | 2.0.0 → 3.0.0 |
| New principle or materially expanded guidance | MINOR | 3.0.0 → 3.1.0 |
| Clarifications, wording, typo fixes | PATCH | 3.0.0 → 3.0.1 |

### Compliance Review

- All PRs MUST verify compliance with this constitution
- Complexity MUST be justified against constitutional principles
- Security violations result in immediate rejection
- Infrastructure changes MUST be tested against success criteria

### Final Authority Statement

This constitution is the **highest authority** for Phase IV.

All plans, tasks, implementations, and evaluations MUST comply with this document.

**If a requirement is not written in a spec, it MUST NOT be implemented.**

The goal is a **cloud-native, hackathon-ready, production-credible local deployment**.

**Version**: 3.0.0 | **Ratified**: 2026-01-08 | **Last Amended**: 2026-01-23
