# API Contract: Tasks (Advanced)

**Base Path**: `/api/{user_id}/tasks`
**Auth**: JWT Bearer token required on all endpoints

## Endpoints

### GET /api/{user_id}/tasks

List tasks with optional search, filter, and sort.

**Query Parameters**:

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| search | string | No | Full-text search across title, description, tags |
| status | string | No | Filter: pending / in_progress / completed / all |
| priority | string | No | Filter: low / medium / high / urgent |
| tags | string | No | Filter: comma-separated tag names |
| due_date_from | datetime | No | Filter: due date range start |
| due_date_to | datetime | No | Filter: due date range end |
| sort_by | string | No | Sort field: due_date / priority / created_at / updated_at |
| sort_order | string | No | asc / desc (default: desc) |

**Response** (200):
```json
{
  "tasks": [
    {
      "id": "uuid",
      "title": "string",
      "description": "string",
      "completed": false,
      "priority": "high",
      "tags": ["work", "urgent"],
      "due_date": "2026-03-01T09:00:00Z",
      "reminder_time": "2026-03-01T08:00:00Z",
      "recurring_rule": null,
      "created_at": "2026-02-07T10:00:00Z",
      "updated_at": "2026-02-07T10:00:00Z"
    }
  ]
}
```

### POST /api/{user_id}/tasks

Create a task with optional advanced attributes.

**Request Body**:
```json
{
  "title": "string (required, max 200)",
  "description": "string (optional, max 2000)",
  "priority": "low|medium|high|urgent (optional, default: medium)",
  "tags": ["string"] ,
  "due_date": "datetime (optional)",
  "reminder_time": "datetime (optional)",
  "recurring_rule": {
    "frequency": "daily|weekly|monthly|custom",
    "interval": 1,
    "day_of_week": 0,
    "cron_expression": "0 9 * * 1"
  }
}
```

**Response** (201): Created task object
**Events emitted**: `task_created` on `todo.events`

### PUT /api/{user_id}/tasks/{task_id}

Update task attributes.

**Request Body**: Partial task object (any fields to update)
**Response** (200): Updated task object
**Events emitted**: `task_updated` on `todo.events`

### DELETE /api/{user_id}/tasks/{task_id}

Delete a task.

**Response** (200): `{"message": "Task deleted"}`
**Events emitted**: `task_deleted` on `todo.events`

### POST /api/{user_id}/tasks/{task_id}/reminder

Set a reminder for a task.

**Request Body**:
```json
{
  "trigger_at": "2026-03-01T08:00:00Z"
}
```

**Response** (201): Reminder object
**Events emitted**: `reminder_scheduled` on `reminder.events`

### DELETE /api/{user_id}/tasks/{task_id}/reminder

Cancel a pending reminder.

**Response** (200): `{"message": "Reminder cancelled"}`
**Events emitted**: `reminder_cancelled` on `reminder.events`

### POST /api/{user_id}/tasks/{task_id}/toggle

Toggle task completion status.

**Response** (200): Updated task object
**Events emitted**: `task_completed` on `todo.events`

## Error Responses

| Status | Description |
|--------|-------------|
| 400 | Invalid input (validation error) |
| 401 | Missing or invalid JWT |
| 403 | User ID mismatch (isolation violation) |
| 404 | Task not found |
| 429 | Rate limit exceeded |
