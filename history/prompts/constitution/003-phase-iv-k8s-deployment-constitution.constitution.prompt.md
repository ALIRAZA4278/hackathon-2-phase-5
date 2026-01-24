---
id: 003
title: Phase IV K8s Deployment Constitution
stage: constitution
date: 2026-01-23
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: developer
command: /sp.constitution
labels: ["kubernetes", "docker", "helm", "phase-iv", "cloud-native", "minikube"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

/sp.constitution

This Constitution defines the highest-authority rules, constraints, and non-negotiable principles for Phase IV of the Hackathon Project: Local Kubernetes Deployment of the Cloud-Native Todo AI Chatbot.

All planning, specification, task generation, and implementation must strictly comply with this Constitution.

Any output that violates this Constitution is invalid.

────────────────────────────────────────
PHASE IV PURPOSE & INTENT
────────────────────────────────────────
Phase IV exists to transform the completed Phase III Todo AI Chatbot into a fully containerized, cloud-native system deployed on a local Kubernetes cluster using Minikube.

This phase evaluates:
- Cloud-native thinking
- Infrastructure automation discipline
- Stateless architecture correctness
- AI-assisted DevOps usage
- Production-grade deployment practices

This phase is NOT about adding new application features.
It is about operational excellence.

────────────────────────────────────────
SCOPE BOUNDARIES
────────────────────────────────────────
INCLUDED:
- Docker containerization of frontend and backend
- Kubernetes deployment using Minikube
- Helm charts for application packaging
- AI-assisted DevOps using:
  - Docker AI Agent (Gordon)
  - kubectl-ai
  - Kagent
- Secure configuration using environment variables
- Stateless deployment validation

EXCLUDED:
- New application logic
- New AI behaviors
- Cloud provider deployments (AWS/GCP/Azure)
- Manual infrastructure configuration outside specs

────────────────────────────────────────
AUTHORITATIVE STACK
────────────────────────────────────────
The only allowed tools and technologies are:

- Docker Desktop (Container runtime)
- Docker AI Agent (Gordon) where available
- Kubernetes (Minikube)
- Helm (Kubernetes package manager)
- kubectl-ai (AI-assisted kubectl)
- Kagent (advanced AI Ops agent)
- Claude Code + Spec-Kit Plus

Manual shell scripting, ad-hoc YAML editing, or undocumented steps are forbidden unless explicitly authorized in specs.

────────────────────────────────────────
INFRASTRUCTURE PRINCIPLES (NON-NEGOTIABLE)
────────────────────────────────────────
1. EVERYTHING IS CONTAINERIZED
   - Frontend and backend must run only inside containers
   - No local execution assumptions

2. STATELESS BY DESIGN
   - Pods must hold no state
   - All state lives in Neon PostgreSQL or external services

3. DECLARATIVE INFRASTRUCTURE
   - Kubernetes resources defined declaratively
   - Helm charts are the single deployment authority

4. REPRODUCIBILITY
   - Any machine with Minikube can reproduce the deployment
   - No hidden steps or manual tweaks

5. AI-ASSISTED OPERATIONS FIRST
   - Prefer Gordon, kubectl-ai, and Kagent for DevOps actions
   - Human-written commands are fallback only

────────────────────────────────────────
DOCKER CONSTITUTION
────────────────────────────────────────
- Each service MUST have its own Dockerfile
- Images must:
  - Be minimal
  - Use explicit base images
  - Expose required ports only
- Secrets MUST NOT be baked into images
- Environment variables injected at runtime

If Docker AI (Gordon) is available:
- It must be used for Dockerfile generation and optimization

────────────────────────────────────────
KUBERNETES CONSTITUTION
────────────────────────────────────────
- Minikube is the only allowed cluster
- Each application component must have:
  - Deployment
  - Service
- Replica count must be configurable
- Pods must be restart-safe
- Readiness and liveness assumptions must exist

kubectl-ai and kagent are first-class operational interfaces.

────────────────────────────────────────
HELM CHART CONSTITUTION
────────────────────────────────────────
- Helm charts are mandatory
- One chart per service (frontend, backend)
- Values.yaml must control:
  - Image name & tag
  - Replicas
  - Environment variables
  - Service configuration

No hard-coded values inside templates.

────────────────────────────────────────
SECURITY & CONFIGURATION RULES
────────────────────────────────────────
- Secrets (JWT secret, Gemini API key, DB URL) must be:
  - Environment variables
  - Kubernetes secrets (not plain YAML)
- No credentials in Git
- No secrets exposed to frontend bundles

────────────────────────────────────────
AI DEVOPS GOVERNANCE
────────────────────────────────────────
Docker AI (Gordon):
- Used for image creation and optimization
- Used for explaining Docker behavior

kubectl-ai:
- Used for deployment, scaling, debugging
- Used for natural-language cluster queries

Kagent:
- Used for cluster health analysis
- Used for optimization suggestions

AI tools must never bypass Kubernetes or Docker security boundaries.

────────────────────────────────────────
VALIDATION & SUCCESS CRITERIA
────────────────────────────────────────
Phase IV is considered successful ONLY if:

- Frontend and backend run successfully in Minikube
- Pods survive restarts without data loss
- Helm install/upgrade works without manual fixes
- Scaling replicas does not break functionality
- Application is accessible via Minikube service
- No local-machine dependencies remain

────────────────────────────────────────
FAILURE CONDITIONS (HARD STOPS)
────────────────────────────────────────
Execution must STOP if:
- Application runs outside Kubernetes
- Secrets are hard-coded
- State is stored in pods
- Helm is bypassed
- Manual fixes are required after deployment
- AI DevOps tools are ignored without justification

────────────────────────────────────────
RELATIONSHIP TO PREVIOUS PHASES
────────────────────────────────────────
Phase IV MUST:
- Deploy the Phase III system as-is
- Preserve all authentication, AI, and MCP behavior
- Not modify application logic

Phase IV does NOT replace or override Phase I–III specs.
It operationalizes them.

────────────────────────────────────────
FINAL AUTHORITY
────────────────────────────────────────
This Constitution overrides:
- All plans
- All tasks
- All assumptions

If ambiguity exists, the output must be made more explicit — never less.

The goal is a **cloud-native, hackathon-ready, production-credible local deployment**.

## Response snapshot

Constitution updated from v2.0.0 to v3.0.0 (MAJOR version bump).

**Key Changes:**
- Added Phase IV Purpose & Intent section
- Added Phase IV Scope Boundaries (In Scope / Out of Scope)
- Added Authoritative Stack table for Phase IV tools
- Added 5 Infrastructure Principles (NON-NEGOTIABLE)
- Added Docker Constitution with Dockerfile requirements and Gordon governance
- Added Kubernetes Constitution with cluster, resource, and deployment specs
- Added Helm Chart Constitution with chart structure and values.yaml requirements
- Extended Security & Configuration Rules for K8s secrets
- Added AI DevOps Governance for Gordon, kubectl-ai, and Kagent
- Added Phase IV Validation & Success Criteria table
- Added Phase IV Failure Conditions (Hard Stops) table
- Added Relationship to Previous Phases section
- Retained inherited Core Principles from Phase II/III
- Extended Technology Stack Compliance with Infrastructure Stack

**Templates Validated:**
- plan-template.md: Constitution Check section compatible
- spec-template.md: Requirements section aligns with infra specs
- tasks-template.md: Phase structure supports Docker/K8s/Helm tasks

## Outcome

- Impact: Major constitution amendment establishing Phase IV governance for Kubernetes deployment
- Tests: N/A (documentation)
- Files: `.specify/memory/constitution.md` updated
- Next prompts: `/sp.specify` for Phase IV feature spec, `/sp.plan` for implementation planning
- Reflection: Phase IV constitution successfully captures all cloud-native deployment requirements with clear boundaries, AI DevOps governance, and success criteria

## Evaluation notes (flywheel)

- Failure modes observed: None - clean amendment
- Graders run and results (PASS/FAIL): PASS - all placeholders filled, version incremented correctly
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test constitution against actual Helm/K8s implementation
