# API Contract: Event Schemas & Topics

All events are published via Dapr pub/sub (HTTP POST to Dapr sidecar).
Consumers subscribe via Dapr subscription endpoints.

## Topics

| Topic | Producer | Consumers |
|-------|----------|-----------|
| todo.events | Backend (task routes) | Audit, Notification |
| reminder.events | Backend (reminder routes) | Reminder Consumer |
| recurring.events | Backend (recurring setup) | Recurring Consumer |
| ai.events | Backend (AI agent) | Audit Consumer |
| audit.events | All consumers | Audit Consumer (persists) |

## Event Payload Schema

### BaseEvent

```json
{
  "event_type": "string",
  "entity_id": "uuid",
  "user_id": "string",
  "timestamp": "2026-02-07T10:00:00Z",
  "idempotency_key": "uuid",
  "payload": {}
}
```

### task_created

```json
{
  "event_type": "task_created",
  "entity_id": "task-uuid",
  "user_id": "user-id",
  "timestamp": "2026-02-07T10:00:00Z",
  "idempotency_key": "uuid",
  "payload": {
    "title": "Buy groceries",
    "priority": "high",
    "tags": ["shopping"],
    "due_date": "2026-02-08T18:00:00Z"
  }
}
```

### task_updated / task_deleted / task_completed

Same structure with `event_type` changed and `payload` containing
the relevant changed fields.

### reminder_scheduled

```json
{
  "event_type": "reminder_scheduled",
  "entity_id": "reminder-uuid",
  "user_id": "user-id",
  "timestamp": "2026-02-07T10:00:00Z",
  "idempotency_key": "uuid",
  "payload": {
    "task_id": "task-uuid",
    "trigger_at": "2026-02-08T17:00:00Z"
  }
}
```

### recurring_spawned

```json
{
  "event_type": "recurring_spawned",
  "entity_id": "new-task-uuid",
  "user_id": "user-id",
  "timestamp": "2026-02-07T10:00:00Z",
  "idempotency_key": "uuid",
  "payload": {
    "parent_task_id": "template-task-uuid",
    "spawned_title": "Weekly Report",
    "next_trigger_at": "2026-02-14T09:00:00Z"
  }
}
```

### ai_tool_called

```json
{
  "event_type": "ai_tool_called",
  "entity_id": "task-uuid-or-null",
  "user_id": "user-id",
  "timestamp": "2026-02-07T10:00:00Z",
  "idempotency_key": "uuid",
  "payload": {
    "tool_name": "create_task",
    "arguments": {"title": "Buy groceries"},
    "result_status": "success",
    "duration_ms": 150
  }
}
```

## Dapr Subscription Configuration

Consumers register subscriptions via HTTP endpoint:

```
GET /dapr/subscribe
```

Returns:
```json
[
  {
    "pubsubname": "pubsub",
    "topic": "todo.events",
    "route": "/events/todo"
  }
]
```

## Retry & Dead-Letter Policy

- Max retries: 3
- Retry delay: exponential backoff (1s, 5s, 30s)
- Dead-letter topic: `{topic}.deadletter`
- Failed events logged to audit.events
