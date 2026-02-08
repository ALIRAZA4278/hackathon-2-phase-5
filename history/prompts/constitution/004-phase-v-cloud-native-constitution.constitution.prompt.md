---
id: 004
title: Phase V Cloud-Native Constitution
stage: constitution
date: 2026-02-07
surface: agent
model: claude-opus-4-6
feature: none
branch: 001-k8s-deployment
user: developer
command: /sp.constitution
labels: ["constitution", "phase-v", "cloud-native", "kafka", "dapr", "kubernetes", "ci-cd"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

/sp.constitution

Project Title:
Phase V — Advanced Cloud-Native AI Todo Chatbot with Event-Driven Architecture, Dapr Runtime, Kafka Streaming, and Multi-Cloud Kubernetes Deployment

Authority Level:
This constitution is the supreme governing rulebook for Phase V implementation. All agents, generated code, infrastructure artifacts, and deployments must comply. If any generated output conflicts with this constitution, the constitution overrides.

Development Method Mandate:
Spec-Driven + Agentic Dev Stack is mandatory.
Workflow must strictly follow:
spec → specify → plan → tasks → agent execution
No manual coding allowed.

All implementation must be executed through Claude Code agents.

---

GLOBAL SYSTEM PURPOSE:

Build an advanced, production-grade, AI-enabled Todo Chatbot platform with:

- Advanced Todo features
- AI tool-calling chatbot
- Event-driven microservices
- Kafka streaming backbone
- Dapr distributed runtime
- Kubernetes-native deployment
- Local Minikube + Cloud K8s rollout
- CI/CD automation
- Observability and safety guardrails

---

PHASE V FUNCTIONAL FEATURE SCOPE (MANDATORY):

Advanced Todo Capabilities:
- Recurring tasks
- Due dates
- Reminder scheduling
- Reminder triggers
- Priority levels
- Tags system
- Search capability
- Filter capability
- Sorting capability

Chatbot Capabilities:
- AI chatbot integrated with backend
- Tool-calling for CRUD
- Structured tool schemas
- Memory-aware conversation
- Guardrail-protected actions

All advanced features must be tool-callable by the AI layer.

---

AI CHATBOT CONSTITUTION:

AI acts as:
- Intent interpreter
- Tool caller
- Structured responder

AI must NOT:
- Directly modify database
- Execute raw queries
- Bypass service layer
- Access secrets
- Perform destructive operations without tool validation

AI MUST:
- Use tool schemas only
- Validate arguments
- Respect user scope
- Return structured JSON-compatible responses
- Log tool calls

Model access allowed via:
OpenAI SDK compatibility + Gemini provider bridge.

---

TOOL CALLING RULES:

Required Tool Groups:

Core Todo Tools:
- create_todo
- update_todo
- delete_todo
- complete_todo
- list_todos

Advanced Tools:
- create_recurring_task
- set_due_date
- schedule_reminder
- set_priority
- add_tags
- search_tasks
- filter_tasks
- sort_tasks

Rules:
- JSON schema enforced
- Strong typing
- Input validation
- Ownership validation
- Idempotency where applicable
- Error-safe responses

AI must never embed CRUD logic — only call tools.

---

EVENT-DRIVEN ARCHITECTURE LAW:

System must be event-driven.

All Todo operations must emit events.

Required Kafka Topics:

- task-events
- reminders
- task-updates
- audit-events
- ai-tool-events

Required Producers:
- Chat API
- Todo service

Required Consumers:
- Notification service
- Recurring task service
- Audit service
- WebSocket sync service

Rules:
- At-least-once delivery
- Idempotent consumers
- Retry policy required
- Dead-letter strategy allowed

Kafka providers allowed:
- Strimzi self-hosted
- Redpanda Cloud
- Confluent Cloud
- Alternative Dapr pubsub backend if Kafka unavailable

---

KAFKA CONSTITUTION:

Kafka usage is mandatory for:
- Reminder triggers
- Recurring task spawning
- Audit logs
- Real-time sync
- Async processing

Event schemas must include:
- event_type
- task_id
- user_id
- timestamp
- payload object

No tightly coupled synchronous chains allowed.

---

DAPR CONSTITUTION (FULL BUILDING BLOCKS REQUIRED):

Dapr must be used in both:
- Minikube deployment
- Cloud K8s deployment

Required Dapr building blocks:

Pub/Sub:
- Kafka abstraction
- No direct Kafka client required in app layer

State Store:
- Conversation memory
- Optional task cache

Service Invocation:
- Frontend → backend calls

Jobs API:
- Reminder scheduling (exact time triggers — not polling)

Bindings:
- Cron or job triggers

Secrets:
- API keys
- DB credentials

Rules:
- Sidecar model only
- YAML components
- No hardcoded infra clients in app code

---

KUBERNETES CONSTITUTION:

Deployments must support:

Local:
- Minikube

Cloud:
- Azure AKS
- Google GKE
- Oracle OKE

All workloads must be deployed via Helm charts.

Helm charts must include:
- Deployments
- Services
- ConfigMaps
- Secret refs
- Resource limits
- Probes
- Replica config
- Image config

Raw kubectl YAML deploy forbidden for final deploy.

---

LOCAL DEPLOYMENT RULES:

Must deploy locally first:

Minikube must run:
- Backend
- Frontend
- AI service
- Kafka / Redpanda
- Dapr
- Supporting services

Dapr init on cluster required.

---

CLOUD DEPLOYMENT RULES:

Must support deployment on:

- AKS
- GKE
- OKE

Kafka options:
- Managed cloud
- Strimzi operator
- Redpanda Cloud

CI/CD pipeline must deploy Helm charts to cloud cluster.

---

CI/CD CONSTITUTION:

GitHub Actions required.

Pipeline must include:

- Build images
- Security scan
- Test stage
- Push registry
- Helm deploy
- Rollback stage

Secrets via:
- GitHub secrets
- K8s secrets
- Dapr secret store

No secrets in code.

---

AI OPS CONSTITUTION:

AI DevOps tools required:

- kubectl-ai
- kagent
- Docker AI (Gordon)

Must be used for:
- Debugging
- Scaling
- Diagnosis
- Optimization

Manual-only ops discouraged.

---

OBSERVABILITY RULES:

Must include:

- AI tool logs
- Event logs
- Pod metrics
- Error tracking

Allowed stack:
- Prometheus
- Grafana
- OpenTelemetry

---

SECURITY & SAFETY GUARDRAILS:

Required:

- Tool validation
- Prompt injection defense
- User isolation
- Rate limiting
- Confirmation flows
- Output filtering

Forbidden:

- Secret exposure
- Cross-user data
- Raw command execution
- Prompt leakage

---

REPOSITORY & SUBMISSION CONSTITUTION:

Repository must include:

- All phases code
- /specs folder
- All spec files
- CLAUDE.md
- README
- Helm charts
- Dapr components
- CI/CD workflows

Deployment links required.

Demo video ≤ 90 seconds.

---

COMPLETION CRITERIA — PHASE V:

Phase V complete only if:

- Advanced features implemented
- AI chatbot tool-calling works
- Kafka event system active
- Dapr runtime integrated
- Minikube deployment working
- Cloud K8s deployment working
- CI/CD active
- Helm-managed deploy
- Guardrails active
- No manual coding performed

---

GOVERNING PHILOSOPHY:

Specs define truth.
Agents implement specs.
AI decides intent.
Tools perform actions.
Events drive system behavior.
Infrastructure is software.
Safety overrides convenience.

End Constitution.

## Response snapshot

Ratified Phase V constitution at `.specify/memory/constitution.md` (v4.0.0). MAJOR version bump from 3.0.0 due to fundamental redefinition of system scope — adding event-driven architecture, Kafka streaming, Dapr runtime, multi-cloud Kubernetes, CI/CD, advanced todo features, and expanded AI chatbot tool-calling. Constitution includes 20+ sections covering: System Mission, Phase V Scope, AI Chatbot Constitution, Tool Calling Rules (13 tools), Event-Driven Architecture Law (5 Kafka topics), Kafka Constitution, Dapr Constitution (6 building blocks), Kubernetes Constitution (Minikube + AKS/GKE/OKE), Helm Chart Constitution, CI/CD Constitution (GitHub Actions, 6 pipeline stages), AI DevOps Constitution, Observability Rules, Security & Safety Guardrails, Infrastructure Principles (6 non-negotiable), Core Principles (5 inherited), Validation & Success Criteria (10 gates), Failure Conditions (13 hard stops), Governing Philosophy, and Governance section.

## Outcome

- ✅ Impact: Constitution v4.0.0 ratified — Phase V governing document established
- 🧪 Tests: No code tests — document artifact
- 📁 Files: .specify/memory/constitution.md (overwritten)
- 🔁 Next prompts: /sp.specify for first Phase V feature spec
- 🧠 Reflection: Comprehensive constitution covering all Phase V subsystems. Templates validated as compatible — no updates needed.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual validation PASS — no unresolved placeholders, version matches report, dates ISO format
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
