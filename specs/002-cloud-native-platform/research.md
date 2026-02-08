# Research: Phase V — Cloud-Native AI Todo Platform

**Branch**: `002-cloud-native-platform` | **Date**: 2026-02-07

## R1: Kafka Provider for Kubernetes

**Decision**: Use Redpanda as the Kafka-compatible broker on Minikube; allow
Confluent Cloud or managed Kafka for cloud deployments.

**Rationale**: Redpanda is Kafka API-compatible, lighter weight for local dev
(single binary, no ZooKeeper/KRaft required for small clusters), and has a
Helm chart for Kubernetes. Strimzi is heavier and requires an operator. Since
Dapr abstracts the pub/sub layer, the app code is broker-agnostic.

**Alternatives Considered**:
- Strimzi Kafka operator: More production-realistic but heavy for Minikube
  (ZooKeeper + Kafka + operator = 3+ pods minimum).
- Confluent Cloud: Managed, but adds external dependency for local dev.
- Dapr in-memory pub/sub: Not persistent; insufficient for production goals.

---

## R2: Dapr State Store Backend

**Decision**: Use Redis as the Dapr state store backend for conversation
memory and optional task cache.

**Rationale**: Redis is the most common Dapr state store, has excellent
Helm support, low latency, and works well for conversation session data.
The existing Neon PostgreSQL remains the primary data store for tasks.

**Alternatives Considered**:
- PostgreSQL state store: Possible but adds coupling to the primary DB.
- In-memory: Not persistent across pod restarts.

---

## R3: Reminder Scheduling Strategy

**Decision**: Use Dapr Jobs API (if available in the target Dapr version)
with fallback to a Kafka-based delayed consumer pattern.

**Rationale**: Dapr Jobs API provides exact-time triggers without polling,
which aligns with the constitution. However, Jobs API may not be GA in all
Dapr versions. Fallback: schedule reminders by publishing to a
`reminder.events` topic with a `trigger_at` field; a dedicated consumer
polls periodically (every 30s) and fires reminders whose trigger_at has
passed.

**Alternatives Considered**:
- Cron binding: Good for recurring but not for one-time reminders at
  arbitrary times.
- External scheduler (Celery, APScheduler): Adds non-Dapr dependency.

---

## R4: AI Service Architecture

**Decision**: Keep AI service embedded within the backend FastAPI service
(not separated into a standalone microservice).

**Rationale**: The existing Phase III agent.py is tightly coupled with
the database session and user context. Separating it would require a
service-to-service API for every tool call, adding latency and complexity
without clear benefit at this scale. The AI service still uses Dapr for
pub/sub (event emission) and state store (conversation memory).

**Alternatives Considered**:
- Separate AI microservice: Cleaner separation but adds 1 more service,
  network hop for every tool call, and deployment complexity.
- Sidecar pattern: AI as a sidecar to backend — unusual and not
  well-supported.

---

## R5: Tag Storage Model

**Decision**: Store tags as a JSON array column on the Task model.

**Rationale**: Tags are simple strings, queries are limited to
contains/overlap checks, and a separate join table adds complexity without
benefit at this scale. PostgreSQL JSON array operators (`@>`, `?`, `?|`)
support efficient filtering.

**Alternatives Considered**:
- Separate Tag table with many-to-many: Normalized but over-engineered
  for string tags on a hackathon project.
- Comma-separated string: Poor for querying.

---

## R6: Recurring Rule Format

**Decision**: Use a JSON object with fields: frequency (daily/weekly/
monthly/custom), interval, day_of_week, day_of_month, cron_expression.
Standard 5-field cron for custom rules.

**Rationale**: A structured JSON object is easier to validate and display
in the UI than raw cron. The cron_expression field handles edge cases.
The recurring consumer parses this to compute `next_trigger_at`.

**Alternatives Considered**:
- Pure cron only: Hard for users to specify via chatbot.
- iCalendar RRULE: Over-complex for this use case.

---

## R7: Priority Representation

**Decision**: Use string enum: "low", "medium", "high", "urgent".

**Rationale**: Human-readable, maps directly to UI labels, easy for the
AI chatbot to parse from natural language. Sorting by priority uses a
predefined ordering (low=1, medium=2, high=3, urgent=4).

**Alternatives Considered**:
- Numeric (1-10): More flexible but harder for AI to interpret and
  display.
- Integer enum (1-4): Less readable in API responses and logs.

---

## R8: Cloud Kubernetes Provider

**Decision**: Target Azure AKS as the primary cloud provider. Support
GKE and OKE as documented alternatives.

**Rationale**: AKS has good free tier options, GitHub Actions integration,
and Dapr is a Microsoft-originated project with first-class AKS support.
The Helm charts are provider-agnostic, so switching to GKE/OKE requires
only values.yaml overrides.

**Alternatives Considered**:
- GKE: Strong but GCP free tier is more limited.
- OKE: Oracle cloud has generous free tier but less community tooling.

---

## R9: Event Consumer Architecture

**Decision**: Implement consumers as separate Python FastAPI services
(lightweight) that subscribe to Dapr pub/sub topics. Each consumer is
its own Kubernetes deployment.

**Rationale**: Separate deployments allow independent scaling and failure
isolation. FastAPI is already in the stack. Each consumer subscribes to
specific Dapr pub/sub topics via HTTP endpoints.

**Alternatives Considered**:
- Single monolithic consumer: Simpler but no isolation.
- Background workers in the backend: Couples event processing with API
  serving.

---

## R10: CI/CD Pipeline Structure

**Decision**: Single GitHub Actions workflow file with job stages:
build → test → scan → push → deploy → smoke-test. Rollback via
`helm rollback` on failure.

**Rationale**: GitHub Actions is the required CI/CD tool. A single
workflow with conditional stages is simpler to maintain. Docker images
pushed to GitHub Container Registry (ghcr.io) for free hosting.

**Alternatives Considered**:
- Separate workflows per service: More parallel but harder to coordinate.
- ArgoCD for GitOps: Good but adds another tool outside the constitution.
