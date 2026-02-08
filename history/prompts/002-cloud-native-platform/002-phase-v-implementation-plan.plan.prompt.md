---
id: 002
title: Phase V Implementation Plan
stage: plan
date: 2026-02-07
surface: agent
model: claude-opus-4-6
feature: 002-cloud-native-platform
branch: 002-cloud-native-platform
user: af912
command: /sp.plan
labels: ["plan", "architecture", "cloud-native", "event-driven", "kubernetes", "dapr", "kafka"]
links:
  spec: specs/002-cloud-native-platform/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-cloud-native-platform/plan.md
  - specs/002-cloud-native-platform/research.md
  - specs/002-cloud-native-platform/data-model.md
  - specs/002-cloud-native-platform/contracts/tasks-api.md
  - specs/002-cloud-native-platform/contracts/tools-api.md
  - specs/002-cloud-native-platform/contracts/events-api.md
  - specs/002-cloud-native-platform/contracts/chat-api.md
  - specs/002-cloud-native-platform/quickstart.md
tests:
  - Constitution gate check (15/15 PASS)
  - Template consistency check (3/3 templates compatible)
---

## Prompt

/sp.plan

Planning Objectives:
1. Translate Phase V specification into a concrete, step-by-step execution plan
2. Define the order of implementation phases for all 14 system components
3. Map dependencies between components (e.g., backend must exist before Kafka events can be emitted)
4. Identify research decisions that must be resolved before implementation begins
5. Produce API contracts and data models that implementation agents can consume without ambiguity
6. Define validation gates at each phase boundary
7. Ensure every phase has clear entry criteria, deliverables, and exit criteria

Execution Strategy: All code is written by AI agents (Claude Code). No manual coding. Agents receive tasks from tasks.md and execute using MCP tools, CLI, and file operations. Each phase completes with validation before the next begins.

14 High-Level Execution Phases:
- Phase 5.1: Architecture Finalization
- Phase 5.2: Backend Model Extension
- Phase 5.3: Advanced Task API
- Phase 5.4: AI Chatbot Enhancement
- Phase 5.5: Event Producer Integration
- Phase 5.6: Kafka/Redpanda Setup
- Phase 5.7: Event Consumer Services
- Phase 5.8: Reminder & Recurring Engine
- Phase 5.9: Dapr Integration
- Phase 5.10: Frontend Enhancement
- Phase 5.11: Docker & Helm Charts
- Phase 5.12: CI/CD Pipeline
- Phase 5.13: Observability Stack
- Phase 5.14: Failure Simulation & Chaos Testing

## Response snapshot

Generated 8 plan artifacts:

1. **plan.md** — Full implementation plan with 14 phases, constitution check (15/15 gates PASS), detailed project structure, service map, and complexity tracking. Each phase has entry criteria, steps, validation gates, and estimated complexity.

2. **research.md** — 10 research decisions resolved:
   - R1: Redpanda over Strimzi/Confluent (lighter, Kafka-compatible)
   - R2: Redis as Dapr state store (proven, simple)
   - R3: Dapr Jobs API for reminders (with cron fallback)
   - R4: AI embedded in backend (not separate service)
   - R5: Tags as JSON array column (PostgreSQL native)
   - R6: Structured JSON for recurring rules (not raw cron)
   - R7: String enum for priority (readable, extensible)
   - R8: AKS as primary cloud target
   - R9: Separate FastAPI services for consumers (isolation)
   - R10: Single GitHub Actions workflow (staged)

3. **data-model.md** — 6 entities: Task (extended), RecurringRule (embedded), Reminder, AuditLog, Conversation, Message. 10 event types across 5 topics.

4. **contracts/tasks-api.md** — Advanced task API with search, filter, sort, reminders, recurring rules.

5. **contracts/tools-api.md** — 13 AI tool schemas (5 core + 8 advanced) with standardized response format.

6. **contracts/events-api.md** — Event schemas, topic mapping, Dapr subscription config, retry/DLQ policy.

7. **contracts/chat-api.md** — Chat endpoints with rate limiting, conversation management, tool_calls response.

8. **quickstart.md** — Local dev setup (Minikube + Dapr + Redpanda + Redis) and cloud deployment (AKS) guide.

## Outcome

- ✅ Impact: Complete implementation plan with 14 phases, 10 research decisions, 6 data models, 4 API contracts, and quickstart guide — ready for `/sp.tasks` generation
- 🧪 Tests: Constitution gate check (15/15 PASS), template consistency (3/3 PASS)
- 📁 Files: 8 files created in specs/002-cloud-native-platform/
- 🔁 Next prompts: `/sp.tasks` to generate actionable task breakdown from plan
- 🧠 Reflection: Explored existing codebase thoroughly before planning. All 10 research decisions resolved with rationale. Plan phases ordered by dependency chain. Constitution alignment verified at every gate.

## Evaluation notes (flywheel)

- Failure modes observed: PowerShell script parameter binding issues on Windows (fixed with named params)
- Graders run and results (PASS/FAIL): Constitution gate check PASS (15/15), Template consistency PASS (3/3)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Generate tasks.md from plan with `/sp.tasks`
