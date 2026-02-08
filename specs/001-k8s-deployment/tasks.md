# Tasks: Local Kubernetes Deployment

**Input**: Design documents from `/specs/001-k8s-deployment/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested. Manual validation via kubectl, helm, and browser access.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Infrastructure**: `frontend/`, `backend/`, `helm/` at repository root
- Docker files in service directories
- Helm charts in `helm/` directory

---

## Phase 1: Setup (Environment & Project Structure)

**Purpose**: Verify environment readiness and create infrastructure directories

- [ ] T001 Verify Docker Desktop is running and Gordon AI Agent is enabled
- [ ] T002 Start Minikube cluster with Docker driver via `minikube start --driver=docker`
- [ ] T003 Verify kubectl context is set to Minikube via `kubectl config current-context`
- [ ] T004 [P] Verify Helm 3.x installation via `helm version`
- [ ] T005 [P] Verify kubectl-ai availability via `kubectl-ai --version`
- [ ] T006 [P] Verify Kagent availability via `kagent --version`
- [x] T007 Create helm/ directory structure at repository root
- [x] T008 [P] Update .gitignore to exclude helm/**/values-local.yaml

**Checkpoint**: Environment ready, all tools verified, directory structure created

---

## Phase 2: Foundational (Docker Infrastructure)

**Purpose**: Create Dockerfiles and .dockerignore files required for ALL user stories

**⚠️ CRITICAL**: No Kubernetes deployment can begin until images are buildable

### Frontend Containerization

- [x] T009 Create frontend/.dockerignore excluding node_modules, .next, .env*
- [x] T010 Create frontend/Dockerfile with multi-stage build (node:20-alpine base)

### Backend Containerization

- [x] T011 [P] Create backend/.dockerignore excluding .venv, __pycache__, .env*
- [x] T012 [P] Update backend/Dockerfile to use port 8000 (currently uses 7860)

### Validation

- [x] T013 Validate frontend Dockerfile uses explicit base image tags (no latest)
- [x] T014 [P] Validate backend Dockerfile uses explicit base image tags (no latest)
- [x] T015 Validate no secrets or credentials in either Dockerfile

**Checkpoint**: Dockerfiles ready for image building

---

## Phase 3: User Story 2 - Build Container Images (Priority: P2) 🎯 FIRST

**Goal**: Build optimized Docker images for frontend and backend using AI assistance

**Independent Test**: Run `docker build` commands and verify images are created with appropriate size

> **Note**: US2 is implemented BEFORE US1 because images are prerequisites for Kubernetes deployment

### Implementation for User Story 2

- [ ] T016 [US2] Configure shell to use Minikube Docker daemon via `eval $(minikube docker-env)`
- [ ] T017 [US2] Build frontend image: `docker build -t todo-frontend:1.0.0 ./frontend`
- [ ] T018 [US2] Build backend image: `docker build -t todo-backend:1.0.0 ./backend`
- [ ] T019 [US2] Verify frontend image size is under 500MB via `docker images todo-frontend`
- [ ] T020 [US2] Verify backend image size is under 300MB via `docker images todo-backend`
- [ ] T021 [US2] Verify images are visible to Minikube via `minikube image ls | grep todo`
- [ ] T022 [US2] Verify multi-stage build used in frontend via `docker history todo-frontend:1.0.0`

**Checkpoint**: Docker images built and available in Minikube

---

## Phase 4: User Story 1 - Deploy to Kubernetes (Priority: P1) 🎯 MVP

**Goal**: Deploy complete application to Minikube using Helm charts

**Independent Test**: Run `helm install` and verify pods reach Running state, app accessible via browser

### Helm Chart Creation

#### Frontend Helm Chart

- [x] T023 [P] [US1] Create helm/frontend/Chart.yaml with name, version, appVersion
- [x] T024 [P] [US1] Create helm/frontend/values.yaml per contracts/frontend-values.yaml schema
- [x] T025 [US1] Create helm/frontend/templates/_helpers.tpl with common template helpers
- [x] T026 [US1] Create helm/frontend/templates/deployment.yaml with pod spec and probes
- [x] T027 [US1] Create helm/frontend/templates/service.yaml with NodePort type
- [x] T028 [US1] Create helm/frontend/templates/configmap.yaml for NEXT_PUBLIC_API_URL

#### Backend Helm Chart

- [x] T029 [P] [US1] Create helm/backend/Chart.yaml with name, version, appVersion
- [x] T030 [P] [US1] Create helm/backend/values.yaml per contracts/backend-values.yaml schema
- [x] T031 [US1] Create helm/backend/templates/_helpers.tpl with common template helpers
- [x] T032 [US1] Create helm/backend/templates/deployment.yaml with pod spec and probes
- [x] T033 [US1] Create helm/backend/templates/service.yaml with ClusterIP type
- [x] T034 [US1] Create helm/backend/templates/configmap.yaml for FRONTEND_URL
- [x] T035 [US1] Create helm/backend/templates/secret.yaml template for sensitive config

#### Helm Validation

- [ ] T036 [US1] Validate frontend chart via `helm lint helm/frontend`
- [ ] T037 [P] [US1] Validate backend chart via `helm lint helm/backend`

### Kubernetes Deployment

- [x] T038 [US1] Create helm/backend/values-local.yaml with actual secrets (gitignored)
- [ ] T039 [US1] Install backend chart: `helm install backend ./helm/backend -f ./helm/backend/values-local.yaml`
- [ ] T040 [US1] Verify backend pod reaches Running state via `kubectl get pods -l app=todo-backend`
- [ ] T041 [US1] Install frontend chart: `helm install frontend ./helm/frontend`
- [ ] T042 [US1] Verify frontend pod reaches Running state via `kubectl get pods -l app=todo-frontend`
- [ ] T043 [US1] Verify services created via `kubectl get services`
- [ ] T044 [US1] Get frontend URL via `minikube service frontend --url`
- [ ] T045 [US1] Validate frontend loads in browser at Minikube service URL
- [ ] T046 [US1] Validate AI chatbot responds to messages (end-to-end test)

**Checkpoint**: Application deployed and accessible via Minikube - MVP COMPLETE

---

## Phase 5: User Story 3 - Scale Replicas (Priority: P3)

**Goal**: Demonstrate horizontal scaling without service interruption

**Independent Test**: Scale replicas and verify application remains accessible

### Implementation for User Story 3

- [ ] T047 [US3] Scale frontend to 3 replicas via kubectl-ai: "scale frontend deployment to 3 replicas"
- [ ] T048 [US3] Verify 3 frontend pods reach Running state via `kubectl get pods -l app=todo-frontend`
- [ ] T049 [US3] Verify application remains accessible during scaling
- [ ] T050 [US3] Scale backend to 2 replicas via `kubectl scale deployment backend --replicas=2`
- [ ] T051 [US3] Verify 2 backend pods reach Running state
- [ ] T052 [US3] Scale frontend down to 1 replica via Helm: `helm upgrade frontend ./helm/frontend --set replicaCount=1`
- [ ] T053 [US3] Verify application continues functioning after scale down

**Checkpoint**: Scaling validated - stateless architecture confirmed

---

## Phase 6: User Story 4 - Survive Pod Restarts (Priority: P3)

**Goal**: Validate stateless architecture survives pod failures

**Independent Test**: Delete pods and verify tasks persist after recreation

### Implementation for User Story 4

- [ ] T054 [US4] Create a test task via the chatbot UI
- [ ] T055 [US4] Delete all backend pods via `kubectl delete pods -l app=todo-backend`
- [ ] T056 [US4] Verify new backend pod starts automatically
- [ ] T057 [US4] Verify test task is still accessible (data persisted in Neon DB)
- [ ] T058 [US4] Delete frontend pod via `kubectl delete pods -l app=todo-frontend`
- [ ] T059 [US4] Verify new frontend pod starts automatically
- [ ] T060 [US4] Verify UI loads and conversation history persists
- [ ] T061 [US4] Execute rolling restart via `kubectl rollout restart deployment frontend backend`
- [ ] T062 [US4] Verify zero downtime during rolling restart

**Checkpoint**: Stateless architecture validated - pods survive restarts

---

## Phase 7: User Story 5 - Helm Upgrade/Rollback (Priority: P4)

**Goal**: Demonstrate Helm release management capabilities

**Independent Test**: Run helm upgrade, verify changes, then rollback and verify restoration

### Implementation for User Story 5

- [ ] T063 [US5] View current Helm releases via `helm list`
- [ ] T064 [US5] Modify frontend replicaCount in values.yaml to 2
- [ ] T065 [US5] Run helm upgrade: `helm upgrade frontend ./helm/frontend`
- [ ] T066 [US5] Verify deployment updates to 2 replicas
- [ ] T067 [US5] View Helm history via `helm history frontend`
- [ ] T068 [US5] Rollback to previous release: `helm rollback frontend 1`
- [ ] T069 [US5] Verify deployment reverts to 1 replica
- [ ] T070 [US5] Verify application still accessible after rollback

**Checkpoint**: Helm lifecycle management validated

---

## Phase 8: User Story 6 - AI-Assisted Operations (Priority: P4)

**Goal**: Demonstrate kubectl-ai and Kagent for cluster management

**Independent Test**: Issue natural language commands and verify correct cluster actions

### Implementation for User Story 6

- [ ] T071 [US6] Query pods via kubectl-ai: "show all pods in the cluster"
- [ ] T072 [US6] Query services via kubectl-ai: "list all services with their ports"
- [ ] T073 [US6] Check logs via kubectl-ai: "show logs for backend pod"
- [ ] T074 [US6] Simulate failure and debug via kubectl-ai: "why is [pod-name] in [state]"
- [ ] T075 [US6] Run Kagent cluster health analysis via `kagent analyze`
- [ ] T076 [US6] Run Kagent resource optimization suggestions via `kagent optimize`
- [ ] T077 [US6] Document AI tool usage examples in quickstart.md

**Checkpoint**: AI-assisted DevOps workflows demonstrated

---

## Phase 9: Polish & Quality Assurance

**Purpose**: Final validation and documentation

- [ ] T078 Verify all success criteria from spec.md (SC-001 through SC-008)
- [ ] T079 [P] Verify no secrets in Git repository via `git grep -i secret`
- [ ] T080 [P] Verify no secrets in Docker image layers via `docker history`
- [ ] T081 Delete all resources and perform fresh deployment test
- [ ] T082 Verify fresh deployment succeeds without manual fixes
- [ ] T083 [P] Update quickstart.md with any corrections discovered
- [ ] T084 Run final Kagent cluster health check

**Checkpoint**: All quality gates passed - Phase IV complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phase 3 (US2 - Images)**: Depends on Phase 2 - BLOCKS US1 deployment
- **Phase 4 (US1 - Deploy)**: Depends on Phase 3 - MVP milestone
- **Phase 5-8 (US3-6)**: All depend on Phase 4 (running deployment)
  - Can run in parallel or sequentially
  - US3, US4 are P3 priority (do before US5, US6)
- **Phase 9 (Polish)**: Depends on all desired user stories complete

### User Story Dependencies

| Story | Priority | Depends On | Can Parallel With |
|-------|----------|------------|-------------------|
| US2 (Images) | P2 | Foundational | None |
| US1 (Deploy) | P1 | US2 | None |
| US3 (Scale) | P3 | US1 | US4 |
| US4 (Restart) | P3 | US1 | US3 |
| US5 (Helm) | P4 | US1 | US6 |
| US6 (AI Ops) | P4 | US1 | US5 |

### Within Each Phase

- Tasks marked [P] can run in parallel
- Tasks without [P] must run sequentially
- Frontend and backend chart creation can run in parallel (T023-T028 || T029-T035)

---

## Parallel Execution Examples

### Phase 2: Foundational Docker Setup

```bash
# These tasks can run in parallel (different files):
Task T009: frontend/.dockerignore
Task T011: backend/.dockerignore
Task T012: backend/Dockerfile

# Then sequential:
Task T010: frontend/Dockerfile (depends on T009)
```

### Phase 4: Helm Chart Creation

```bash
# Frontend and backend charts can be created in parallel:
# Stream A:
Task T023: helm/frontend/Chart.yaml
Task T024: helm/frontend/values.yaml
Task T025-T028: frontend templates

# Stream B:
Task T029: helm/backend/Chart.yaml
Task T030: helm/backend/values.yaml
Task T031-T035: backend templates

# Then validation in parallel:
Task T036: helm lint frontend
Task T037: helm lint backend
```

### Phase 5-8: Post-Deployment User Stories

```bash
# After MVP (US1) is complete, these can run in parallel:
# Stream A: US3 (Scaling) + US4 (Restarts)
# Stream B: US5 (Helm ops) + US6 (AI ops)

# Or sequentially by priority:
# P3 first: US3 → US4
# P4 next: US5 → US6
```

---

## Implementation Strategy

### MVP First (Recommended)

1. **Phase 1**: Setup (verify environment)
2. **Phase 2**: Foundational (create Dockerfiles)
3. **Phase 3**: US2 (build images)
4. **Phase 4**: US1 (deploy to Minikube)
5. **STOP and VALIDATE**: Application accessible, chatbot responds

**MVP Scope**: Phases 1-4 (Tasks T001-T046)

### Incremental Delivery

1. MVP (Phases 1-4) → Deployed application
2. Add US3 + US4 (Phases 5-6) → Scaling and resilience validated
3. Add US5 + US6 (Phases 7-8) → Operations workflows demonstrated
4. Phase 9 → Final polish and QA

### Task Count Summary

| Phase | Story | Task Range | Count |
|-------|-------|------------|-------|
| 1 | Setup | T001-T008 | 8 |
| 2 | Foundational | T009-T015 | 7 |
| 3 | US2 (Images) | T016-T022 | 7 |
| 4 | US1 (Deploy) | T023-T046 | 24 |
| 5 | US3 (Scale) | T047-T053 | 7 |
| 6 | US4 (Restart) | T054-T062 | 9 |
| 7 | US5 (Helm) | T063-T070 | 8 |
| 8 | US6 (AI Ops) | T071-T077 | 7 |
| 9 | Polish | T078-T084 | 7 |
| **Total** | | | **84** |

---

## Notes

- [P] tasks = different files, no dependencies
- [US#] label maps task to specific user story for traceability
- Manual validation required (no automated tests specified)
- Commit after each phase or logical group
- Stop at any checkpoint to validate independently
- Use kubectl-ai for operations when possible (constitution requirement)
