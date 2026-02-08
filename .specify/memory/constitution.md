<!--
================================================================================
SYNC IMPACT REPORT
================================================================================
Version Change: 3.0.0 → 4.0.0 (MAJOR - Phase V Cloud-Native AI Todo Platform)

Modified Principles:
  - System Mission → Redefined from "deploy Phase III as-is" to
    "build advanced event-driven AI Todo platform with multi-cloud K8s"
  - Technology Stack Compliance → Extended with Kafka, Dapr, multi-cloud K8s
  - Kubernetes Constitution → Extended from Minikube-only to multi-cloud
    (AKS, GKE, OKE)
  - Security & Configuration → Extended with AI safety guardrails,
    prompt injection defense, rate limiting
  - AI DevOps Governance → Extended with full AI Ops constitution

Added Sections:
  - Phase V Purpose & Intent
  - Phase V Functional Feature Scope
  - AI Chatbot Constitution
  - Tool Calling Rules (Core + Advanced)
  - Event-Driven Architecture Law
  - Kafka Constitution
  - Dapr Constitution (Full Building Blocks)
  - CI/CD Constitution (GitHub Actions)
  - Observability Rules
  - Security & Safety Guardrails (expanded)
  - Phase V Completion Criteria
  - Phase V Failure Conditions
  - Governing Philosophy

Removed Sections:
  - Phase IV Purpose & Intent (superseded by Phase V)
  - Phase IV Scope Boundaries (superseded by Phase V)
  - Phase IV Validation & Success Criteria (replaced)
  - Phase IV Failure Conditions (replaced)
  - "Out of Scope" items that are now in-scope (CI/CD, cloud deploy, etc.)

Templates Requiring Updates:
  ✅ plan-template.md - Constitution Check section is generic; compatible
  ✅ spec-template.md - Requirements section aligns with expanded scope
  ✅ tasks-template.md - Phase structure supports event-driven/infra tasks

Follow-up TODOs: None

================================================================================
-->

# Hackathon Todo – Phase V Constitution

**Phase Name**: Advanced Cloud-Native AI Todo Chatbot with Event-Driven
Architecture, Dapr Runtime, Kafka Streaming, and Multi-Cloud Kubernetes
Deployment
**Development Model**: Spec-Driven + Agentic Dev Stack
**Implementation Tooling**: Claude Code + Spec-Kit Plus + AI DevOps Agents

**Authority Level**: This constitution is the supreme governing rulebook
for Phase V implementation. All agents, generated code, infrastructure
artifacts, and deployments MUST comply. If any generated output conflicts
with this constitution, the constitution overrides.

This constitution serves as the single source of truth for how the system
is designed, built, deployed, and operated. All plans, tasks,
implementations, and evaluations MUST comply with this document.

## System Mission

Build an advanced, production-grade, AI-enabled Todo Chatbot platform
with:

- Advanced Todo features (recurring, due dates, reminders, priorities,
  tags, search, filter, sort)
- AI tool-calling chatbot with structured schemas
- Event-driven microservices architecture
- Kafka streaming backbone
- Dapr distributed runtime
- Kubernetes-native deployment (local + multi-cloud)
- CI/CD automation via GitHub Actions
- Observability and safety guardrails

The system MUST be built using the Agentic Dev Stack workflow with NO
manual coding, relying strictly on Spec-Kit Plus, Claude Code, and AI
DevOps agents.

## Phase V Purpose & Intent

Phase V exists to transform the completed Phase III/IV Todo AI Chatbot
into an advanced, event-driven, cloud-native platform deployed across
local and cloud Kubernetes clusters with full operational maturity.

**Goals:**
- Implement advanced todo features (recurring, reminders, priorities,
  tags, search, filter, sort)
- Build AI chatbot with structured tool-calling for all operations
- Establish event-driven architecture with Kafka streaming
- Integrate Dapr runtime for distributed building blocks
- Deploy to Minikube (local) and cloud K8s (AKS/GKE/OKE)
- Automate CI/CD with GitHub Actions
- Implement observability and safety guardrails

## Phase V Scope Boundaries

### In Scope (Phase V)

- Advanced todo capabilities (recurring tasks, due dates, reminders,
  priorities, tags, search, filter, sort)
- AI chatbot with tool-calling for all CRUD and advanced operations
- Memory-aware conversation with guardrail-protected actions
- Event-driven architecture with Kafka topics and consumers
- Dapr runtime integration (pub/sub, state store, service invocation,
  jobs API, bindings, secrets)
- Docker containerization of all services
- Kubernetes deployment via Helm charts
- Local deployment on Minikube
- Cloud deployment on AKS, GKE, or OKE
- CI/CD pipeline via GitHub Actions
- Observability (Prometheus, Grafana, OpenTelemetry)
- AI DevOps tooling (kubectl-ai, kagent, Docker AI Gordon)

### Out of Scope (Phase V)

- Mobile applications
- Third-party integrations beyond specified stack
- Multi-tenancy beyond user isolation
- Manual infrastructure configuration outside specs

## Phase V Functional Feature Scope (MANDATORY)

### Advanced Todo Capabilities

All of the following MUST be implemented:

- Recurring tasks
- Due dates
- Reminder scheduling
- Reminder triggers
- Priority levels
- Tags system
- Search capability
- Filter capability
- Sorting capability

### Chatbot Capabilities

- AI chatbot integrated with backend
- Tool-calling for CRUD and advanced operations
- Structured tool schemas (JSON schema enforced)
- Memory-aware conversation
- Guardrail-protected actions

All advanced features MUST be tool-callable by the AI layer.

## AI Chatbot Constitution

### AI Role

AI acts as:
- Intent interpreter
- Tool caller
- Structured responder

### AI Prohibitions

AI MUST NOT:
- Directly modify database
- Execute raw queries
- Bypass service layer
- Access secrets
- Perform destructive operations without tool validation

### AI Obligations

AI MUST:
- Use tool schemas only
- Validate arguments
- Respect user scope
- Return structured JSON-compatible responses
- Log tool calls

### Model Access

Model access allowed via OpenAI SDK compatibility + Gemini provider
bridge.

## Tool Calling Rules

### Core Todo Tools (REQUIRED)

| Tool | Purpose |
|------|---------|
| create_todo | Create a new task |
| update_todo | Update an existing task |
| delete_todo | Delete a task |
| complete_todo | Mark a task as complete |
| list_todos | List user's tasks |

### Advanced Tools (REQUIRED)

| Tool | Purpose |
|------|---------|
| create_recurring_task | Create a task with recurrence |
| set_due_date | Set or update due date |
| schedule_reminder | Schedule a reminder |
| set_priority | Set task priority level |
| add_tags | Add tags to a task |
| search_tasks | Search tasks by keyword |
| filter_tasks | Filter tasks by criteria |
| sort_tasks | Sort tasks by field |

### Tool Rules

- JSON schema MUST be enforced for all tools
- Strong typing MUST be used for all parameters
- Input validation MUST be performed before execution
- Ownership validation MUST verify user scope
- Idempotency MUST be applied where applicable
- Error-safe responses MUST be returned on failure
- AI MUST NEVER embed CRUD logic — only call tools

## Event-Driven Architecture Law

The system MUST be event-driven. All Todo operations MUST emit events.

### Required Kafka Topics

| Topic | Purpose |
|-------|---------|
| task-events | Task lifecycle events |
| reminders | Reminder scheduling events |
| task-updates | Task modification events |
| audit-events | Audit trail events |
| ai-tool-events | AI tool invocation events |

### Required Producers

- Chat API
- Todo service

### Required Consumers

- Notification service
- Recurring task service
- Audit service
- WebSocket sync service

### Event Rules

- At-least-once delivery MUST be guaranteed
- Consumers MUST be idempotent
- Retry policy MUST be defined for each consumer
- Dead-letter strategy MUST be available for failed events
- No tightly coupled synchronous chains are allowed

### Event Schema

All events MUST include:
- `event_type`: string identifier
- `task_id`: UUID of the affected task
- `user_id`: UUID of the owning user
- `timestamp`: ISO 8601 timestamp
- `payload`: object with event-specific data

## Kafka Constitution

Kafka usage is MANDATORY for:
- Reminder triggers
- Recurring task spawning
- Audit logs
- Real-time sync
- Async processing

### Kafka Providers Allowed

- Strimzi self-hosted (on K8s)
- Redpanda Cloud
- Confluent Cloud
- Alternative Dapr pub/sub backend if Kafka unavailable

## Dapr Constitution

Dapr MUST be used in both Minikube and cloud K8s deployments.

### Required Dapr Building Blocks

| Building Block | Purpose |
|---------------|---------|
| Pub/Sub | Kafka abstraction — no direct Kafka client in app |
| State Store | Conversation memory, optional task cache |
| Service Invocation | Frontend → backend calls |
| Jobs API | Reminder scheduling (exact time triggers, not polling) |
| Bindings | Cron or job triggers |
| Secrets | API keys, DB credentials |

### Dapr Rules

- Sidecar model MUST be used exclusively
- YAML components MUST define all Dapr configuration
- No hardcoded infrastructure clients in application code
- Application layer MUST interact only through Dapr SDK/HTTP APIs

## Kubernetes Constitution

### Deployment Targets

| Environment | Platform | Status |
|------------|----------|--------|
| Local | Minikube | REQUIRED |
| Cloud | Azure AKS | REQUIRED (at least one) |
| Cloud | Google GKE | REQUIRED (at least one) |
| Cloud | Oracle OKE | REQUIRED (at least one) |

At minimum, one cloud provider deployment MUST be demonstrated.

### Workload Requirements

All workloads MUST be deployed via Helm charts. Raw `kubectl` YAML
deployment is FORBIDDEN for final deployments.

### Cluster Services (Minikube)

Minikube MUST run:
- Backend service
- Frontend service
- AI service
- Kafka / Redpanda
- Dapr runtime
- Supporting services (consumers, schedulers)

Dapr init on cluster MUST be performed.

### Resource Requirements

Each application component MUST have:

| Resource | Required |
|----------|----------|
| Deployment | Yes |
| Service | Yes |
| ConfigMap | As needed |
| Secret | As needed |
| Resource requests | Yes |
| Resource limits | Recommended |
| Readiness probes | SHOULD |
| Liveness probes | SHOULD |

### Pod Specifications

- MUST be restart-safe (RestartPolicy: Always)
- MUST have resource requests defined
- Replicas MUST be configurable via Helm values
- MUST support scaling without breaking functionality

## Helm Chart Constitution

### Chart Structure

Helm charts MUST include:
- Deployments
- Services
- ConfigMaps
- Secret refs
- Resource limits
- Probes
- Replica config
- Image config

### Values.yaml Requirements

Values.yaml MUST control:

| Parameter | Required |
|-----------|----------|
| image.repository | Yes |
| image.tag | Yes |
| replicaCount | Yes |
| service.type | Yes |
| service.port | Yes |
| env.* | Yes |
| resources.requests | Yes |
| resources.limits | Recommended |

No hard-coded values inside templates. All configuration MUST flow
through values.yaml.

### Chart Metadata

Chart.yaml MUST include:
- name: Service identifier
- version: Chart version (semver)
- appVersion: Application version
- description: Brief chart description

## CI/CD Constitution

GitHub Actions is REQUIRED for all CI/CD.

### Pipeline Stages (MANDATORY)

| Stage | Purpose |
|-------|---------|
| Build images | Container image creation |
| Security scan | Vulnerability scanning |
| Test stage | Automated testing |
| Push registry | Push to container registry |
| Helm deploy | Deploy via Helm to K8s cluster |
| Rollback stage | Automated rollback on failure |

### Secrets Management (CI/CD)

- GitHub Secrets for pipeline credentials
- Kubernetes Secrets for runtime credentials
- Dapr secret store for application secrets
- No secrets in code — EVER

## AI DevOps Constitution

### Required AI DevOps Tools

| Tool | Purpose | Status |
|------|---------|--------|
| kubectl-ai | AI-assisted kubectl operations | Required |
| kagent | Advanced AI Ops agent | Required |
| Docker AI (Gordon) | Image creation/optimization | Preferred |

### Usage Requirements

AI DevOps tools MUST be used for:
- Debugging pod and deployment issues
- Scaling operations
- Cluster diagnosis
- Optimization recommendations

Manual-only operations are discouraged. AI tools MUST be preferred.

### Constraints

- MUST NOT delete production resources without confirmation
- MUST NOT modify system namespaces
- MUST NOT bypass RBAC when configured
- Read-only analysis MUST be preferred for diagnostics

## Observability Rules

### Required Observability

| Capability | Status |
|-----------|--------|
| AI tool call logs | REQUIRED |
| Event/Kafka logs | REQUIRED |
| Pod metrics | REQUIRED |
| Error tracking | REQUIRED |

### Allowed Observability Stack

- Prometheus (metrics collection)
- Grafana (dashboards/visualization)
- OpenTelemetry (distributed tracing)

## Security & Safety Guardrails

### Required Guardrails

| Guardrail | Purpose |
|-----------|---------|
| Tool validation | Validate all AI tool inputs |
| Prompt injection defense | Prevent prompt manipulation |
| User isolation | No cross-user data access |
| Rate limiting | Prevent abuse |
| Confirmation flows | Verify destructive actions |
| Output filtering | Sanitize AI responses |

### Forbidden Practices

- Secret exposure in code, logs, or images
- Cross-user data access
- Raw command execution by AI
- Prompt leakage to end users
- Hard-coded credentials
- Unvalidated tool arguments

### Secrets Management

Secrets (JWT secret, API keys, Database URL) MUST be:
- Stored as Kubernetes Secrets (not plain ConfigMaps)
- Injected as environment variables
- NEVER committed to Git
- NEVER exposed to frontend bundles
- Managed through Dapr secret store where applicable

## Docker Constitution

### Dockerfile Requirements

Each service MUST have its own Dockerfile following these rules:

**Image Design:**
- Use explicit base image tags (no `latest`)
- Use multi-stage builds to minimize final image size
- Expose only the required port
- Set appropriate user (non-root where possible)

**Security:**
- Secrets MUST NOT be baked into images
- No sensitive data in build args
- No credentials in Dockerfile comments or labels

**Build Context:**
- Include appropriate .dockerignore
- Minimize build context size
- Cache layers effectively

## Infrastructure Principles (NON-NEGOTIABLE)

### I. Everything is Containerized

All services MUST run only inside containers. No local execution
assumptions for deployment.

### II. Stateless by Design

Pods MUST hold no state. All state lives in external databases or
Dapr state stores.

### III. Declarative Infrastructure

Kubernetes resources MUST be defined declaratively. Helm charts are
the single deployment authority.

### IV. Reproducibility

Any machine with Minikube MUST be able to reproduce the local
deployment. Cloud deployments MUST be reproducible via CI/CD.

### V. AI-Assisted Operations First

Prefer AI DevOps tools for all operational tasks. Human-written
commands are fallback only.

### VI. Event-Driven Communication

Services MUST communicate asynchronously through Kafka/Dapr pub-sub.
Direct synchronous chains between services are FORBIDDEN except for
request-response API calls.

## Core Principles (Inherited from Phase II/III/IV)

### I. Spec-Driven Development (NON-NEGOTIABLE)

All development MUST follow the Agentic Development Stack workflow:

1. Write or update specifications
2. Generate a technical plan from specs
3. Break the plan into tasks
4. Delegate implementation to Claude Code
5. Review outputs and iterate by updating specs

**Rules:**
- Claude Code MUST NEVER implement features not defined in specs
- Specifications ALWAYS override assumptions
- If a requirement is not written in a spec, it MUST NOT be implemented

### II. Zero Manual Coding

The developer's role is specification authorship, not code authorship.

**Rules:**
- All code, Dockerfiles, Helm charts, Kubernetes manifests, CI/CD
  workflows, and Dapr components MUST be written by Claude Code
- Manual edits are forbidden
- Developer interaction is limited to: writing specs, reviewing
  outputs, approving deployments
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
- AI tool calls MUST validate user ownership
- Event payloads MUST include user_id for scoping

### V. Technology Stack Compliance

The technology stack is fixed and non-negotiable.

**Application Stack:**
- Frontend: Next.js 16+ / TypeScript / Tailwind CSS / Better Auth
- Backend: Python FastAPI / SQLModel / OpenAI Agents SDK
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth / JWT

**AI Stack:**
- OpenAI SDK compatibility + Gemini provider bridge
- Structured tool-calling with JSON schemas

**Infrastructure Stack:**
- Container Runtime: Docker Desktop
- Orchestration: Kubernetes (Minikube + AKS/GKE/OKE)
- Packaging: Helm charts
- Event Streaming: Kafka (Strimzi/Redpanda/Confluent)
- Distributed Runtime: Dapr
- CI/CD: GitHub Actions
- AI DevOps: Gordon, kubectl-ai, Kagent

**Observability Stack:**
- Prometheus / Grafana / OpenTelemetry

## Authoritative Stack (Phase V)

| Tool | Purpose | Status |
|------|---------|--------|
| Docker Desktop | Container runtime | Required |
| Docker AI (Gordon) | Image optimization | Preferred |
| Minikube | Local Kubernetes cluster | Required |
| AKS / GKE / OKE | Cloud Kubernetes | Required (1+) |
| Helm | Kubernetes package manager | Required |
| Kafka / Redpanda | Event streaming | Required |
| Dapr | Distributed runtime | Required |
| GitHub Actions | CI/CD pipeline | Required |
| kubectl-ai | AI-assisted kubectl | Required |
| Kagent | AI Ops agent | Required |
| Prometheus | Metrics | Required |
| Grafana | Dashboards | Required |
| OpenTelemetry | Tracing | Required |
| Claude Code + Spec-Kit Plus | Development workflow | Required |

## Phase V Validation & Success Criteria

Phase V is considered successful ONLY if ALL of the following are met:

| Criterion | Validation Method |
|-----------|-------------------|
| Advanced features implemented | All 9 features functional |
| AI chatbot tool-calling works | All core + advanced tools respond |
| Kafka event system active | Events emitted and consumed |
| Dapr runtime integrated | All building blocks operational |
| Minikube deployment working | `kubectl get pods` all Running |
| Cloud K8s deployment working | At least 1 cloud cluster active |
| CI/CD active | GitHub Actions pipeline passes |
| Helm-managed deployment | `helm install` succeeds |
| Guardrails active | Validation, injection defense working |
| No manual coding performed | All code from Claude Code agents |

## Phase V Failure Conditions (Hard Stops)

Execution MUST STOP if:

| Violation | Severity |
|-----------|----------|
| AI embeds CRUD logic directly | CRITICAL |
| Cross-user data access possible | CRITICAL |
| Secrets hard-coded in code/images | CRITICAL |
| State stored in pods | CRITICAL |
| Direct Kafka client in app (bypassing Dapr) | HIGH |
| Helm bypassed for deployment | HIGH |
| Manual fixes required after deployment | HIGH |
| No event emission on Todo operations | HIGH |
| CI/CD pipeline absent | HIGH |
| AI DevOps tools ignored without justification | MEDIUM |
| Images use `latest` tag | MEDIUM |
| No resource requests defined | LOW |
| Observability stack absent | LOW |

## Relationship to Previous Phases

### Phase V MUST:

- Build upon the Phase III application and Phase IV infrastructure
- Preserve all authentication, AI, and user isolation behavior
- Extend application features (advanced todo, tool-calling)
- Extend infrastructure (Kafka, Dapr, multi-cloud, CI/CD)

### Phase V does NOT replace:

- Phase I (Backend Foundation)
- Phase II (Full-Stack Integration)
- Phase III (AI Chatbot System)
- Phase IV (Local K8s Deployment)

**Phase V operationalizes and extends Phases I-IV into a
production-grade, event-driven, multi-cloud platform.**

## Repository & Submission Requirements

Repository MUST include:

- All phases code
- `/specs` folder with all spec files
- `CLAUDE.md` project instructions
- `README.md` with setup and usage
- Helm charts for all services
- Dapr component YAML files
- CI/CD workflow files (.github/workflows/)
- Deployment links (cloud cluster URLs)

Demo video MUST be ≤ 90 seconds.

## Governing Philosophy

- Specs define truth
- Agents implement specs
- AI decides intent
- Tools perform actions
- Events drive system behavior
- Infrastructure is software
- Safety overrides convenience

## Governance

### Amendment Process

1. Proposed amendments MUST be documented in a spec
2. Amendments MUST include rationale and impact analysis
3. Constitution version MUST be incremented per semantic versioning
4. All dependent artifacts MUST be updated for consistency

### Versioning Policy

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Backward-incompatible principle removal/redefinition | MAJOR | 3.0.0 → 4.0.0 |
| New principle or materially expanded guidance | MINOR | 4.0.0 → 4.1.0 |
| Clarifications, wording, typo fixes | PATCH | 4.0.0 → 4.0.1 |

### Compliance Review

- All PRs MUST verify compliance with this constitution
- Complexity MUST be justified against constitutional principles
- Security violations result in immediate rejection
- Infrastructure changes MUST be tested against success criteria
- AI tool implementations MUST validate against tool calling rules

### Final Authority Statement

This constitution is the **highest authority** for Phase V.

All plans, tasks, implementations, and evaluations MUST comply with
this document.

**If a requirement is not written in a spec, it MUST NOT be
implemented.**

The goal is a **cloud-native, event-driven, AI-powered,
production-grade Todo platform**.

**Version**: 4.0.0 | **Ratified**: 2026-01-08 | **Last Amended**: 2026-02-07
