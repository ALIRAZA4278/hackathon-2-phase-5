# Data Model: Phase V — Cloud-Native AI Todo Platform

**Branch**: `002-cloud-native-platform` | **Date**: 2026-02-07

## Entities

### Task (extend existing)

Extends existing Task model with advanced attributes.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes (auto) | Primary key |
| user_id | string | Yes | Owner (from JWT) |
| title | string | Yes | Task title (max 200 chars) |
| description | string | No | Task description (max 2000 chars) |
| completed | boolean | Yes | Completion status (default: false) |
| priority | enum | No | low / medium / high / urgent (default: medium) |
| tags | string[] | No | List of tag strings (default: []) |
| due_date | datetime | No | Due date (ISO 8601) |
| reminder_time | datetime | No | Reminder trigger time |
| recurring_rule | JSON | No | Recurrence configuration (see RecurringRule) |
| created_at | datetime | Yes (auto) | Creation timestamp (UTC) |
| updated_at | datetime | Yes (auto) | Last update timestamp (UTC) |

**New fields** (Phase V): priority, tags, due_date, reminder_time, recurring_rule

### RecurringRule (embedded JSON in Task)

Stored as a JSON object within Task.recurring_rule.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| frequency | enum | Yes | daily / weekly / monthly / custom |
| interval | integer | No | Repeat every N periods (default: 1) |
| day_of_week | integer | No | 0=Monday .. 6=Sunday (for weekly) |
| day_of_month | integer | No | 1-31 (for monthly) |
| cron_expression | string | No | 5-field cron (for custom) |
| next_trigger_at | datetime | Yes | Next scheduled spawn time |
| is_active | boolean | Yes | Whether rule is active (default: true) |

### Reminder (new model)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes (auto) | Primary key |
| task_id | UUID | Yes | Related task |
| user_id | string | Yes | Owner (from JWT) |
| trigger_at | datetime | Yes | When to fire the reminder |
| status | enum | Yes | pending / triggered / cancelled |
| created_at | datetime | Yes (auto) | Creation timestamp |

**State transitions**: pending → triggered (on fire) or pending → cancelled (on delete)

### AuditLog (new model)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes (auto) | Primary key |
| action | string | Yes | Operation performed (e.g., task_created) |
| entity_type | string | Yes | Entity affected (e.g., task, reminder) |
| entity_id | UUID | Yes | ID of affected entity |
| user_id | string | Yes | Who performed the action |
| timestamp | datetime | Yes (auto) | When the action occurred |
| details | JSON | No | Additional context |

### Conversation (existing, no changes)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes (auto) | Primary key |
| user_id | string | Yes | Owner |
| created_at | datetime | Yes (auto) | Creation timestamp |
| updated_at | datetime | Yes (auto) | Last activity |

### Message (existing, no changes)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes (auto) | Primary key |
| user_id | string | Yes | Owner |
| conversation_id | UUID | Yes | Parent conversation |
| role | string | Yes | user / assistant |
| content | string | Yes | Message text |
| created_at | datetime | Yes (auto) | Timestamp |

## Event Schemas

### BaseEvent

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| event_type | string | Yes | Event identifier |
| entity_id | UUID | Yes | Affected entity ID |
| user_id | string | Yes | Owning user |
| timestamp | datetime | Yes | Event time (ISO 8601) |
| payload | JSON | Yes | Event-specific data |
| idempotency_key | UUID | Yes | Dedup key |

### Event Types

| Event Type | Topic | Trigger |
|-----------|-------|---------|
| task_created | todo.events | Task creation |
| task_updated | todo.events | Task modification |
| task_deleted | todo.events | Task deletion |
| task_completed | todo.events | Task completion toggle |
| reminder_scheduled | reminder.events | Reminder set |
| reminder_triggered | reminder.events | Reminder fired |
| reminder_cancelled | reminder.events | Reminder cancelled |
| recurring_spawned | recurring.events | New recurring instance |
| ai_tool_called | ai.events | AI tool invocation |
| audit_entry | audit.events | Any auditable action |

## Relationships

- Task → Reminder: One-to-many (a task can have one pending reminder)
- Task → RecurringRule: One-to-one (embedded JSON)
- Task → AuditLog: One-to-many (via entity_id)
- Conversation → Message: One-to-many
- All entities scoped by user_id (user isolation)
