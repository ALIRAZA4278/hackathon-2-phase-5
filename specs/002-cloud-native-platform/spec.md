# Feature Specification: Phase V — Advanced Cloud-Native AI Todo Platform

**Feature Branch**: `002-cloud-native-platform`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Phase V — Advanced Cloud-Native AI Todo Chatbot with Kafka Event Streaming, Dapr Runtime, and Multi-Cloud Kubernetes Deployment"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Advanced Task Management (Priority: P1)

A user opens the Todo dashboard and creates a task with a due date, priority level, and tags. They set a reminder for 1 hour before the due date. They use the search bar to find tasks by keyword and apply filters (by priority, by tag, by status). They sort their task list by due date or priority. They create a recurring task that automatically spawns new instances on a schedule.

**Why this priority**: Advanced task management is the core user-facing feature of Phase V. Without it, the platform has no new functional value over Phase III/IV. Every other feature (AI tool-calling, events, Kafka) depends on these task attributes existing.

**Independent Test**: Can be fully tested by creating tasks with due dates, priorities, tags, and recurring rules through the UI, then verifying search, filter, and sort work correctly. Delivers immediate user value as a standalone feature.

**Acceptance Scenarios**:

1. **Given** a logged-in user, **When** they create a task with title, due date (2026-03-01), priority (high), and tags (["work", "urgent"]), **Then** the task appears in their list with all attributes visible.
2. **Given** a user with 20 tasks of varying priorities, **When** they filter by priority "high", **Then** only high-priority tasks are displayed.
3. **Given** a user with tagged tasks, **When** they search for "work", **Then** all tasks matching the keyword in title, description, or tags are returned.
4. **Given** a user with tasks having different due dates, **When** they sort by due date ascending, **Then** tasks appear ordered by earliest due date first.
5. **Given** a user creates a recurring task with rule "every Monday", **When** Monday arrives, **Then** a new task instance is automatically created.
6. **Given** a user sets a reminder for a task, **When** the reminder time arrives, **Then** the user receives a notification.
7. **Given** a user with no tasks matching a filter, **When** they apply that filter, **Then** an empty state message is displayed.

---

### User Story 2 - AI Chatbot with Tool-Calling (Priority: P2)

A user opens the chat interface and types natural language commands like "Create a task called 'Buy groceries' with high priority due tomorrow" or "Show me all urgent tasks due this week" or "Set a reminder for my meeting prep task at 3pm". The AI chatbot interprets intent, calls the appropriate tool, and returns a structured response confirming the action.

**Why this priority**: The AI chatbot is the differentiating feature of this platform. It makes all advanced features accessible via natural language, which is the primary interaction model. It depends on User Story 1 (task attributes) being implemented first.

**Independent Test**: Can be tested by sending natural language messages through the chat UI and verifying that the AI correctly interprets intent, calls the right tool, and returns accurate responses. Each tool call can be verified against the database state.

**Acceptance Scenarios**:

1. **Given** a logged-in user in the chat interface, **When** they type "Create a task called 'Finish report' with high priority", **Then** the AI creates the task via the create_task tool and confirms with the task details.
2. **Given** a user with existing tasks, **When** they type "Show me all my high priority tasks", **Then** the AI calls filter_tasks and returns a formatted list.
3. **Given** a user, **When** they type "Set a reminder for 'Finish report' at 3pm tomorrow", **Then** the AI calls schedule_reminder and confirms the reminder is set.
4. **Given** a user, **When** they type "Make 'Finish report' a recurring task every Friday", **Then** the AI calls create_recurring and confirms the recurrence rule.
5. **Given** a user, **When** they type "Search for tasks about groceries", **Then** the AI calls search_tasks and returns matching results.
6. **Given** a user asks something ambiguous like "Delete everything", **Then** the AI requests confirmation before executing any destructive action.
7. **Given** a user in a multi-turn conversation, **When** they say "Mark it as done" (referring to a previously discussed task), **Then** the AI uses conversation context to identify and complete the correct task.

---

### User Story 3 - Event-Driven Notifications and Sync (Priority: P3)

When a user creates, updates, or deletes a task through either the UI or the chatbot, an event is emitted. Consumers process these events to trigger reminders, spawn recurring tasks, maintain audit trails, and keep the UI synchronized in real-time.

**Why this priority**: Event-driven architecture is the backbone infrastructure. While users do not directly interact with Kafka or Dapr, the system behavior they expect (reminders firing on time, recurring tasks appearing automatically, audit trails existing) depends on this event pipeline working correctly.

**Independent Test**: Can be tested by performing task operations (create, update, delete) and verifying that: (a) events appear in Kafka topics, (b) reminder consumer triggers notifications at the right time, (c) recurring consumer spawns new tasks, (d) audit consumer logs all operations.

**Acceptance Scenarios**:

1. **Given** a user creates a task, **When** the operation completes, **Then** a `task_created` event is published to the `todo.events` topic containing the task details, user_id, and timestamp.
2. **Given** a task with a reminder set, **When** the reminder time arrives, **Then** the reminder consumer triggers and the user is notified.
3. **Given** a recurring task template, **When** the recurrence schedule triggers, **Then** the recurring consumer creates a new task instance and emits a `recurring_spawned` event.
4. **Given** any task operation, **When** the operation completes, **Then** an audit event is logged to the `audit.events` topic.
5. **Given** a user using the AI chatbot to modify a task, **When** the tool executes, **Then** an `ai_tool_called` event is emitted to the `ai.events` topic.

---

### User Story 4 - Kubernetes Deployment and Operations (Priority: P4)

A DevOps engineer deploys the entire platform to a local Minikube cluster using Helm charts. They then deploy the same platform to a cloud Kubernetes cluster (AKS, GKE, or OKE) via the CI/CD pipeline. The deployment includes all services: frontend, backend, AI service, Kafka, Dapr sidecars, and event consumers. The CI/CD pipeline builds images, runs tests, scans for vulnerabilities, pushes to a registry, deploys via Helm, and supports rollback.

**Why this priority**: Deployment and operations are the final validation layer. The platform must run in Kubernetes with all infrastructure components (Kafka, Dapr) working together. This depends on all previous stories being functionally complete.

**Independent Test**: Can be tested by running `helm install` on Minikube and verifying all pods reach Running state, services are accessible, and end-to-end functionality works. Cloud deployment is tested via the CI/CD pipeline completing successfully.

**Acceptance Scenarios**:

1. **Given** a fresh Minikube cluster with Dapr initialized, **When** `helm install` is run for all services, **Then** all pods reach Running state within 5 minutes.
2. **Given** a deployed Minikube cluster, **When** a user accesses the frontend via `minikube service`, **Then** the application is fully functional (create tasks, chat, search, filter).
3. **Given** a code push to the main branch, **When** the CI/CD pipeline runs, **Then** images are built, tested, scanned, pushed to the registry, and deployed to the cloud cluster.
4. **Given** a failed deployment, **When** rollback is triggered, **Then** the previous working version is restored.
5. **Given** a running cluster, **When** AI DevOps tools (kubectl-ai, kagent) are used, **Then** they can diagnose, scale, and optimize the deployment.
6. **Given** a deployed cluster, **When** Prometheus and Grafana are accessed, **Then** metrics, logs, and dashboards are available for all services.

---

### Edge Cases

- What happens when a user creates a task with a due date in the past? The system accepts it but flags it as overdue immediately.
- What happens when Kafka is temporarily unavailable? Events are retried with exponential backoff; the dead-letter queue captures failed events after max retries.
- What happens when the AI model returns an invalid tool call? The tool execution layer validates the call against the schema and returns an error response to the user.
- What happens when a recurring task rule generates a task that conflicts with an existing one? Each spawned task gets a unique identity; no deduplication is enforced.
- What happens when a user deletes a task that has a pending reminder? The reminder becomes a no-op when it fires (the task no longer exists).
- What happens when the Dapr sidecar is not available? The service fails health checks and Kubernetes restarts the pod.
- What happens when a user exceeds rate limits on the chat endpoint? A 429 response is returned with a retry-after header.

## Requirements *(mandatory)*

### Functional Requirements

**Advanced Task Attributes:**

- **FR-001**: System MUST support task priority levels (low, medium, high, urgent).
- **FR-002**: System MUST support tags as a list of strings per task.
- **FR-003**: System MUST support due dates as date-time values.
- **FR-004**: System MUST support reminder scheduling with a specific trigger time.
- **FR-005**: System MUST support recurring task rules (daily, weekly, monthly, custom cron-like expressions).
- **FR-006**: System MUST support full-text search across task title, description, and tags.
- **FR-007**: System MUST support filtering tasks by status, priority, tags, due date range, and combinations thereof.
- **FR-008**: System MUST support sorting tasks by due date, priority, created date, and updated date in ascending or descending order.

**AI Chatbot:**

- **FR-009**: System MUST accept natural language input from authenticated users.
- **FR-010**: System MUST interpret user intent and map it to one or more tool calls.
- **FR-011**: System MUST validate all tool call arguments against defined schemas before execution.
- **FR-012**: System MUST maintain conversation context within a session for multi-turn interactions.
- **FR-013**: System MUST require explicit user confirmation before executing destructive operations (delete, bulk operations).
- **FR-014**: System MUST return structured, human-readable responses after tool execution.
- **FR-015**: System MUST log all AI tool calls as events.

**Tool Calling:**

- **FR-016**: System MUST implement 5 core tools: create_task, update_task, delete_task, complete_task, list_tasks.
- **FR-017**: System MUST implement 8 advanced tools: set_due_date, schedule_reminder, create_recurring, set_priority, add_tags, search_tasks, filter_tasks, sort_tasks.
- **FR-018**: All tools MUST validate user ownership before executing.
- **FR-019**: All tools MUST return error-safe structured responses.
- **FR-020**: Tools MUST NOT embed CRUD logic directly — they MUST call backend service endpoints.

**Event-Driven Architecture:**

- **FR-021**: All task write operations (create, update, delete, complete) MUST emit events.
- **FR-022**: Events MUST be published to designated topics via Dapr pub/sub.
- **FR-023**: Event payloads MUST include event_type, entity_id, user_id, timestamp, and payload object.
- **FR-024**: Consumers MUST be idempotent (processing the same event twice produces the same result).
- **FR-025**: Failed events MUST be routed to a dead-letter queue after retry exhaustion.

**Kafka & Dapr:**

- **FR-026**: System MUST use Dapr pub/sub for all event messaging (no direct Kafka client in application code).
- **FR-027**: System MUST use Dapr state store for conversation memory.
- **FR-028**: System MUST use Dapr service invocation for frontend-to-backend communication.
- **FR-029**: System MUST use Dapr Jobs API or equivalent for reminder scheduling (no polling).
- **FR-030**: System MUST use Dapr secret store for API keys and database credentials.

**Deployment:**

- **FR-031**: System MUST deploy to Minikube via Helm charts.
- **FR-032**: System MUST deploy to at least one cloud Kubernetes provider (AKS, GKE, or OKE) via CI/CD.
- **FR-033**: Helm charts MUST support install, upgrade, and rollback operations.
- **FR-034**: All configuration MUST flow through Helm values (no hard-coded values in templates).
- **FR-035**: Secrets MUST be stored as Kubernetes Secrets and injected as environment variables.

**CI/CD:**

- **FR-036**: System MUST have a CI/CD pipeline with build, test, scan, push, deploy, and rollback stages.
- **FR-037**: Pipeline MUST use secure secret stores only (no secrets in code or pipeline logs).

**Observability:**

- **FR-038**: System MUST expose metrics via Prometheus-compatible endpoints.
- **FR-039**: System MUST provide dashboards for service health, event flow, and AI tool usage.
- **FR-040**: System MUST integrate distributed tracing across services.

**Security:**

- **FR-041**: All API endpoints MUST require valid JWT authentication.
- **FR-042**: All database queries MUST filter by authenticated user_id.
- **FR-043**: AI tool calls MUST validate user ownership of target resources.
- **FR-044**: System MUST implement rate limiting on the chat endpoint.
- **FR-045**: System MUST implement prompt injection defense for AI inputs.

### Key Entities

- **Task**: Represents a user's todo item. Key attributes: title, description, status (pending/in_progress/completed), priority (low/medium/high/urgent), tags (string array), due_date, reminder_time, recurring_rule, user_id, created_at, updated_at.
- **RecurringRule**: Defines the recurrence pattern for a task. Key attributes: frequency (daily/weekly/monthly/custom), interval, day_of_week, day_of_month, cron_expression, next_trigger_at, parent_task_id.
- **Reminder**: A scheduled notification tied to a task. Key attributes: task_id, user_id, trigger_at, status (pending/triggered/cancelled).
- **Conversation**: Represents a chat session. Key attributes: user_id, messages (list), thread_id, created_at, last_active_at.
- **Event**: Represents a system event. Key attributes: event_type, entity_id, user_id, timestamp, payload, topic.
- **AuditLog**: An immutable record of system operations. Key attributes: action, entity_type, entity_id, user_id, timestamp, details.

### Assumptions

- The existing Phase III authentication system (Better Auth + JWT) is retained as-is.
- The existing database is the primary data store; new tables/columns are added for advanced attributes.
- Dapr is the sole infrastructure abstraction layer; services do not use direct Kafka clients.
- The Gemini provider bridge (from Phase III) is retained for AI model access.
- Rate limiting uses standard token bucket or sliding window approach (200 requests/minute per user on chat).
- Recurring task cron expressions follow standard 5-field cron syntax.
- Reminder notifications are delivered via the frontend UI (no email/SMS integration).
- One cloud provider deployment is sufficient to satisfy the cloud K8s requirement.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a task with due date, priority, tags, and reminder in under 30 seconds.
- **SC-002**: Users can find any task using search, filter, or sort within 2 seconds of interaction.
- **SC-003**: The AI chatbot correctly interprets and executes user intent for at least 90% of standard task management commands.
- **SC-004**: Reminders trigger within 60 seconds of the scheduled time.
- **SC-005**: Recurring tasks spawn new instances within 60 seconds of the recurrence schedule.
- **SC-006**: Events flow from producer to consumer within 5 seconds under normal load.
- **SC-007**: All pods reach Running state within 5 minutes of `helm install`.
- **SC-008**: The CI/CD pipeline completes build-to-deploy in under 15 minutes.
- **SC-009**: System supports at least 50 concurrent users without degradation.
- **SC-010**: Zero cross-user data exposure across all test scenarios.
- **SC-011**: AI chatbot correctly blocks or requests confirmation for 100% of destructive operations.
- **SC-012**: Rollback restores the previous working version within 2 minutes.
