# Tasks: Phase V — Cloud-Native AI Todo Platform

**Input**: Design documents from `/specs/002-cloud-native-platform/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the feature specification. Test tasks are omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/` (FastAPI), `frontend/` (Next.js), `consumers/` (event consumers), `dapr/`, `helm/`, `.github/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependency updates, and shared configuration

- [x] T001 Add Phase V Python dependencies (dapr-client, prometheus-client, opentelemetry-sdk, httpx) to backend/requirements.txt
- [x] T002 [P] Create event module directory structure: backend/app/events/__init__.py, backend/app/events/schemas.py, backend/app/events/topics.py, backend/app/events/producer.py
- [x] T003 [P] Create consumer service directory structure: consumers/reminder/, consumers/recurring/, consumers/audit/, consumers/notification/ each with __init__.py and requirements.txt
- [x] T004 [P] Create Dapr component directory structure: dapr/components/ and dapr/config.yaml
- [x] T005 [P] Create TypeScript types file for advanced task attributes in frontend/types/task.ts
- [x] T006 Extend backend/app/config.py with Dapr-related settings (DAPR_HTTP_PORT, DAPR_GRPC_PORT) and keep backward compatibility

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Extend Task model in backend/app/models.py with new fields: priority (str, default "medium"), tags (JSON, default []), due_date (datetime, optional), reminder_time (datetime, optional), recurring_rule (JSON, optional)
- [x] T008 Create Reminder model in backend/app/models.py with fields: id, task_id, user_id, trigger_at, status (pending/triggered/cancelled), created_at
- [x] T009 Create AuditLog model in backend/app/models.py with fields: id, action, entity_type, entity_id, user_id, timestamp, details (JSON)
- [x] T010 Extend TaskCreate schema in backend/app/schemas.py with optional fields: priority, tags, due_date, reminder_time, recurring_rule
- [x] T011 Extend TaskUpdate schema in backend/app/schemas.py to accept partial updates for all new fields (priority, tags, due_date, reminder_time, recurring_rule)
- [x] T012 Extend TaskResponse schema in backend/app/schemas.py to include priority, tags, due_date, reminder_time, recurring_rule fields
- [x] T013 Create ReminderResponse and AuditLogResponse Pydantic schemas in backend/app/schemas.py
- [x] T014 Define event payload schemas (BaseEvent, TaskEvent, ReminderEvent, RecurringEvent, AuditEvent, AIToolEvent) in backend/app/events/schemas.py per contracts/events-api.md
- [x] T015 [P] Define topic name constants (todo.events, reminder.events, recurring.events, ai.events, audit.events) in backend/app/events/topics.py
- [x] T016 Create Dapr pub/sub event publisher in backend/app/events/producer.py using httpx to POST to Dapr sidecar HTTP API (http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{pubsubname}/{topic})
- [x] T017 Sync TypeScript Task interface in frontend/types/task.ts with extended backend TaskResponse (add priority, tags, due_date, reminder_time, recurring_rule fields)
- [x] T018 Update Task interface in frontend/lib/api.ts to import from frontend/types/task.ts and add TaskCreate/TaskUpdate with advanced fields

**Checkpoint**: Foundation ready — extended models, schemas, event infrastructure, and TypeScript types in place. User story implementation can now begin.

---

## Phase 3: User Story 1 — Advanced Task Management (Priority: P1) MVP

**Goal**: Users can create tasks with priority, tags, due dates, reminders, and recurring rules. Users can search, filter, and sort their task list.

**Independent Test**: Create tasks with all advanced attributes via API and UI. Verify search returns keyword matches, filters narrow results by priority/status/tags/date, and sort reorders correctly.

### Backend Implementation for US1

- [x] T019 [US1] Extend GET /{user_id}/tasks in backend/app/routes/tasks.py with query params: search (str), status (str), priority (str), tags (str), due_date_from (datetime), due_date_to (datetime), sort_by (str), sort_order (str) per contracts/tasks-api.md
- [x] T020 [US1] Extend POST /{user_id}/tasks in backend/app/routes/tasks.py to accept and persist priority, tags, due_date, reminder_time, recurring_rule from extended TaskCreate schema
- [x] T021 [US1] Extend PUT /{user_id}/tasks/{task_id} in backend/app/routes/tasks.py to accept partial updates for all advanced fields
- [x] T022 [US1] Create POST /{user_id}/tasks/{task_id}/reminder endpoint in backend/app/routes/tasks.py to set a reminder (creates Reminder record, emits reminder_scheduled event)
- [x] T023 [US1] Create DELETE /{user_id}/tasks/{task_id}/reminder endpoint in backend/app/routes/tasks.py to cancel a pending reminder
- [x] T024 [US1] Create POST /{user_id}/tasks/{task_id}/toggle endpoint in backend/app/routes/tasks.py (rename from PATCH .../complete to POST .../toggle per contract)
- [x] T025 [US1] Integrate event emission into task routes: emit task_created, task_updated, task_deleted, task_completed events via producer.py after each write operation
- [x] T026 [US1] Update backend/app/main.py to register any new route prefixes if needed

### Frontend Implementation for US1

- [x] T027 [P] [US1] Create TaskFilters component in frontend/components/todo/TaskFilters.tsx with priority dropdown, status tabs, tag chips, and date range picker
- [x] T028 [P] [US1] Create TaskSearch component in frontend/components/todo/TaskSearch.tsx with debounced search input that calls GET /tasks?search=
- [x] T029 [P] [US1] Create TaskSort component in frontend/components/todo/TaskSort.tsx with sort_by (due_date, priority, created_at, updated_at) and sort_order (asc/desc) dropdowns
- [x] T030 [US1] Extend TaskForm in frontend/components/todo/TaskForm.tsx to include priority selector, tags input, due date picker, and reminder time picker
- [x] T031 [US1] Extend TaskCard in frontend/components/todo/TaskCard.tsx to display priority badge, tags, due date, and reminder indicator
- [x] T032 [US1] Extend TaskList in frontend/components/todo/TaskList.tsx to wire up TaskFilters, TaskSearch, TaskSort components and pass query params to API
- [x] T033 [US1] Extend frontend/lib/api.ts tasksApi.list() to accept and pass search, filter, and sort query parameters
- [x] T034 [US1] Add tasksApi.setReminder() and tasksApi.cancelReminder() methods in frontend/lib/api.ts

**Checkpoint**: User Story 1 complete — advanced task management with search, filter, sort working via UI and API. MVP deliverable.

---

## Phase 4: User Story 2 — AI Chatbot with Tool-Calling (Priority: P2)

**Goal**: AI chatbot interprets natural language, calls the correct tool from 13 available tools, and returns structured responses. Destructive operations require confirmation.

**Independent Test**: Send natural language commands via chat UI and verify AI routes to correct tool, returns accurate responses, and blocks unconfirmed destructive actions.

### Tool Implementation for US2

- [x] T035 [US2] Add set_due_date tool function in backend/app/mcp_tools.py that updates a task's due_date field with ownership validation
- [x] T036 [P] [US2] Add schedule_reminder tool function in backend/app/mcp_tools.py that creates a Reminder record and emits reminder_scheduled event
- [x] T037 [P] [US2] Add create_recurring tool function in backend/app/mcp_tools.py that sets recurring_rule JSON on a task with ownership validation
- [x] T038 [P] [US2] Add set_priority tool function in backend/app/mcp_tools.py that updates a task's priority field with enum validation
- [x] T039 [P] [US2] Add add_tags tool function in backend/app/mcp_tools.py that appends tags to a task's tags array with dedup
- [x] T040 [P] [US2] Add filter_tasks tool function in backend/app/mcp_tools.py that filters by status, priority, tags, and date range
- [x] T041 [P] [US2] Add sort_tasks tool function in backend/app/mcp_tools.py that sorts tasks by due_date, priority, created_at, or updated_at
- [x] T042 [US2] Update existing add_task tool in backend/app/mcp_tools.py to accept and persist priority, tags, due_date, reminder_time parameters
- [x] T043 [US2] Update existing search_tasks tool in backend/app/mcp_tools.py to also search in tags array (not just title/description)
- [x] T044 [US2] Update existing list_tasks, toggle_task_completion, delete_task tools in backend/app/mcp_tools.py to include new fields in response data

### Agent Configuration for US2

- [x] T045 [US2] Add 7 new tool definitions (set_due_date, schedule_reminder, create_recurring, set_priority, add_tags, filter_tasks, sort_tasks) to TOOLS array in backend/app/agent.py per contracts/tools-api.md
- [x] T046 [US2] Update existing tool definitions in TOOLS array (add_task, search_tasks, list_tasks) with new parameter schemas in backend/app/agent.py
- [x] T047 [US2] Register all 7 new tool functions in TOOL_FUNCTIONS dispatcher map in backend/app/agent.py
- [x] T048 [US2] Update SYSTEM_PROMPT in backend/app/agent.py with all 13 tool capabilities, confirmation rules for delete, and advanced feature instructions
- [x] T049 [US2] Add event emission on every tool call: after execute_tool() returns, publish ai_tool_called event to ai.events topic via producer.py in backend/app/agent.py

### Safety Guardrails for US2

- [x] T050 [US2] Add confirmation flow for delete_task tool: validate confirmed=false on first call, return "please confirm" message, only delete when confirmed=true in backend/app/mcp_tools.py
- [x] T051 [US2] Add input sanitization for AI chat messages (strip potential prompt injection patterns) in backend/app/routes/chat.py
- [x] T052 [US2] Add rate limiting middleware (200 req/min per user) on POST /{user_id}/chat endpoint in backend/app/routes/chat.py

**Checkpoint**: User Story 2 complete — AI chatbot with 13 tools, safety guardrails, and event emission working.

---

## Phase 5: User Story 3 — Event-Driven Notifications and Sync (Priority: P3)

**Goal**: All task operations emit events. Consumer services process events for reminders, recurring task spawning, audit logging, and notifications.

**Independent Test**: Perform task operations and verify events appear in Kafka topics. Check that reminder consumer triggers on time, recurring consumer spawns tasks, and audit consumer logs all operations.

### Dapr Configuration for US3

- [x] T053 [US3] Create Dapr pub/sub component YAML for Redpanda in dapr/components/pubsub.yaml with Kafka-compatible configuration
- [x] T054 [P] [US3] Create Dapr state store component YAML for Redis in dapr/components/statestore.yaml
- [x] T055 [P] [US3] Create Dapr secret store component YAML for Kubernetes secrets in dapr/components/secretstore.yaml
- [x] T056 [P] [US3] Create Dapr cron binding component YAML for recurring task checks in dapr/components/binding-cron.yaml
- [x] T057 [P] [US3] Create Dapr configuration file at dapr/config.yaml with tracing and metrics enabled

### Backend Dapr Integration for US3

- [x] T058 [US3] Create Dapr subscription endpoint GET /dapr/subscribe in backend/app/routes/events.py that returns subscription list for todo.events, reminder.events, recurring.events
- [x] T059 [US3] Create event handler POST /events/todo endpoint in backend/app/routes/events.py (receives Dapr pub/sub events, logs for debugging)
- [x] T060 [US3] Register events router in backend/app/main.py

### Consumer Services for US3

- [x] T061 [US3] Create audit consumer service in consumers/audit/main.py: FastAPI app that subscribes to todo.events, ai.events, and audit.events topics, persists AuditLog records to database
- [x] T062 [P] [US3] Create notification consumer service in consumers/notification/main.py: FastAPI app that subscribes to todo.events topic and logs notification events (placeholder for real notifications)
- [x] T063 [US3] Create reminder consumer service in consumers/reminder/main.py: FastAPI app that subscribes to reminder.events topic, checks trigger_at time, fires notification when due, updates Reminder status to triggered
- [x] T064 [US3] Create recurring consumer service in consumers/recurring/main.py: FastAPI app that subscribes to recurring.events topic, computes next occurrence from recurring_rule, creates new Task via backend API, emits recurring_spawned event
- [x] T065 [US3] Add idempotency key tracking in each consumer service to prevent duplicate event processing (use in-memory set or Dapr state store)

### Consumer Dockerfiles for US3

- [x] T066 [P] [US3] Create consumers/audit/Dockerfile using Python 3.11-slim base with non-root user
- [x] T067 [P] [US3] Create consumers/notification/Dockerfile using Python 3.11-slim base with non-root user
- [x] T068 [P] [US3] Create consumers/reminder/Dockerfile using Python 3.11-slim base with non-root user
- [x] T069 [P] [US3] Create consumers/recurring/Dockerfile using Python 3.11-slim base with non-root user

**Checkpoint**: User Story 3 complete — events flow from backend through Dapr pub/sub to Kafka/Redpanda, consumed by 4 independent services.

---

## Phase 6: User Story 4 — Kubernetes Deployment and Operations (Priority: P4)

**Goal**: Deploy all services to Minikube via Helm charts with Dapr sidecars. CI/CD pipeline automates build-to-deploy. Observability stack provides metrics and dashboards.

**Independent Test**: Run `helm install` on Minikube, verify all pods Running, access frontend, create tasks, use chatbot, check events in Redpanda, view Grafana dashboards.

### Docker Images for US4

- [x] T070 [US4] Update backend/Dockerfile to multi-stage build with non-root user, health check, and .dockerignore
- [x] T071 [P] [US4] Verify frontend/Dockerfile works with current Next.js version (update if needed)
- [x] T072 [P] [US4] Create .dockerignore files for backend/, frontend/, and each consumers/*/ directory

### Infrastructure Helm Charts for US4

- [x] T073 [US4] Create helm/infrastructure/redpanda/ Helm chart (Chart.yaml, values.yaml, templates/deployment.yaml, templates/service.yaml) for Redpanda broker
- [x] T074 [P] [US4] Create helm/infrastructure/redis/ Helm chart (Chart.yaml, values.yaml, templates/deployment.yaml, templates/service.yaml) for Redis state store
- [x] T075 [P] [US4] Create helm/infrastructure/observability/ Helm chart with Prometheus and Grafana (Chart.yaml, values.yaml, templates/)

### Application Helm Charts for US4

- [x] T076 [US4] Update helm/backend/ chart: add Dapr sidecar annotations (dapr.io/enabled, dapr.io/app-id, dapr.io/app-port), new env vars (DAPR_HTTP_PORT), resource limits, liveness/readiness probes
- [x] T077 [US4] Update helm/frontend/ chart: add Dapr sidecar annotations for service invocation, update ConfigMap with new env vars
- [x] T078 [P] [US4] Create helm/consumers/reminder/ Helm chart with Dapr sidecar annotations and subscription to reminder.events
- [x] T079 [P] [US4] Create helm/consumers/recurring/ Helm chart with Dapr sidecar annotations and subscription to recurring.events
- [x] T080 [P] [US4] Create helm/consumers/audit/ Helm chart with Dapr sidecar annotations and subscription to todo.events, ai.events, audit.events
- [x] T081 [P] [US4] Create helm/consumers/notification/ Helm chart with Dapr sidecar annotations and subscription to todo.events
- [x] T082 [US4] Create helm/todo-app/ umbrella chart (Chart.yaml with dependencies on backend, frontend, consumers, infrastructure charts, values.yaml)

### CI/CD Pipeline for US4

- [x] T083 [US4] Create .github/workflows/ci-cd.yaml with build job: build Docker images for backend, frontend, and all 4 consumers
- [x] T084 [US4] Add test job to .github/workflows/ci-cd.yaml: run health check validation on built images
- [x] T085 [US4] Add scan job to .github/workflows/ci-cd.yaml: container image vulnerability scanning (trivy or similar)
- [x] T086 [US4] Add push job to .github/workflows/ci-cd.yaml: push images to ghcr.io (GitHub Container Registry)
- [x] T087 [US4] Add deploy job to .github/workflows/ci-cd.yaml: helm upgrade --install to AKS cluster with rollback on failure
- [x] T088 [US4] Add rollback job to .github/workflows/ci-cd.yaml: helm rollback triggered on deploy failure

### Observability for US4

- [x] T089 [US4] Add Prometheus metrics endpoint (/metrics) to backend/app/main.py using prometheus-client library
- [x] T090 [P] [US4] Add Prometheus metrics endpoints to each consumer service (consumers/*/main.py)
- [x] T091 [US4] Add structured JSON logging to backend and all consumer services
- [x] T092 [US4] Create Grafana dashboard JSON for service health, event flow rates, and AI tool usage in helm/infrastructure/observability/templates/

### Kubernetes Validation for US4

- [x] T093 [US4] Run helm lint on all charts (backend, frontend, consumers, infrastructure, umbrella) — 9/9 passed, 0 failures
- [ ] T094 [US4] Apply Dapr component YAMLs to Minikube cluster: kubectl apply -f dapr/components/ — RUNTIME: requires cluster
- [ ] T095 [US4] Deploy full stack to Minikube via helm install todo-app helm/todo-app/ and verify all pods Running — RUNTIME: requires cluster
- [ ] T096 [US4] Verify end-to-end flow: create task via UI → event emitted → consumer processes → audit logged — RUNTIME: requires cluster

**Checkpoint**: User Story 4 complete — full platform deployed to Minikube with Dapr, Kafka, CI/CD, and observability.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Security hardening, failure validation, and final integration

- [x] T097 Verify user isolation across all new endpoints and tools (priority, tags, reminders, recurring) — ensure WHERE user_id = :jwt_user_id on every query
- [x] T098 Verify secrets management: no secrets in code, Dockerfiles, Helm templates, or CI/CD logs
- [ ] T099 Kill backend pod and verify Kubernetes auto-recovery (pod restarts, no data loss) — RUNTIME: requires cluster
- [ ] T100 Stop Redpanda broker and verify retry/DLQ behavior (events retried 3 times with exponential backoff) — RUNTIME: requires cluster
- [ ] T101 Test Helm rollback: deploy broken version, trigger rollback, verify previous version restored — RUNTIME: requires cluster
- [ ] T102 Run end-to-end acceptance validation for all 4 user stories per quickstart.md validation checklist — RUNTIME: requires cluster
- [ ] T103 Run quickstart.md validation: follow quickstart steps on fresh Minikube cluster and verify all checkpoints pass — RUNTIME: requires cluster

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on Foundational + US1 backend (needs extended models/routes for tools)
- **User Story 3 (Phase 5)**: Depends on Foundational + US1 event emission integration (T025)
- **User Story 4 (Phase 6)**: Depends on all previous phases (needs all services to containerize and deploy)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ── BLOCKS ALL ──┐
    ↓                                    │
Phase 3 (US1: Advanced Tasks) ◄─────────┘
    ↓
Phase 4 (US2: AI Chatbot) ← needs US1 models/routes
    ↓
Phase 5 (US3: Event-Driven) ← needs US1 event emission
    ↓
Phase 6 (US4: K8s Deploy) ← needs all services built
    ↓
Phase 7 (Polish)
```

### Within Each User Story

- Models/schemas before routes/services
- Backend before frontend
- Core implementation before event integration
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1** (all [P] tasks):
- T002, T003, T004, T005 can run in parallel (different directories)

**Phase 2**:
- T014, T015 can run in parallel (different files)

**Phase 3 (US1)** frontend:
- T027, T028, T029 can run in parallel (different component files)

**Phase 4 (US2)** tools:
- T036, T037, T038, T039, T040, T041 can run in parallel (different tool functions in same file, but independent)

**Phase 5 (US3)** Dapr + Consumers:
- T054, T055, T056, T057 can run in parallel (different YAML files)
- T062 can run parallel with T061 (different consumer services)
- T066, T067, T068, T069 can run in parallel (different Dockerfiles)

**Phase 6 (US4)** Helm + CI/CD:
- T071, T072 can run parallel with T070
- T074, T075 can run parallel with T073
- T078, T079, T080, T081 can run in parallel (different chart directories)
- T090 can run parallel with T089

---

## Parallel Example: User Story 1

```bash
# Launch all frontend components for US1 together (different files):
Task T027: "Create TaskFilters in frontend/components/todo/TaskFilters.tsx"
Task T028: "Create TaskSearch in frontend/components/todo/TaskSearch.tsx"
Task T029: "Create TaskSort in frontend/components/todo/TaskSort.tsx"
```

## Parallel Example: User Story 2

```bash
# Launch all new tool functions together (independent implementations):
Task T036: "Add schedule_reminder tool in backend/app/mcp_tools.py"
Task T037: "Add create_recurring tool in backend/app/mcp_tools.py"
Task T038: "Add set_priority tool in backend/app/mcp_tools.py"
Task T039: "Add add_tags tool in backend/app/mcp_tools.py"
Task T040: "Add filter_tasks tool in backend/app/mcp_tools.py"
Task T041: "Add sort_tasks tool in backend/app/mcp_tools.py"
```

## Parallel Example: User Story 3

```bash
# Launch all consumer Dockerfiles together (different directories):
Task T066: "Create consumers/audit/Dockerfile"
Task T067: "Create consumers/notification/Dockerfile"
Task T068: "Create consumers/reminder/Dockerfile"
Task T069: "Create consumers/recurring/Dockerfile"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test US1 independently — create tasks with priority/tags/due_date, search, filter, sort
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → AI chatbot with 13 tools
4. Add User Story 3 → Test independently → Event-driven pipeline
5. Add User Story 4 → Test independently → Full K8s deployment
6. Each story adds value without breaking previous stories

### Sequential Strategy (Single Agent)

With a single Claude Code agent executing sequentially:

1. Phase 1 → Phase 2 → Phase 3 (US1) → VALIDATE MVP
2. Phase 4 (US2) → VALIDATE AI chatbot
3. Phase 5 (US3) → VALIDATE event pipeline
4. Phase 6 (US4) → VALIDATE K8s deployment
5. Phase 7 → FINAL VALIDATION

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- US2 depends on US1 backend (extended models/routes/tools need the new fields)
- US3 depends on US1 event emission (consumers need events flowing)
- US4 depends on all services existing (to containerize and deploy)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
