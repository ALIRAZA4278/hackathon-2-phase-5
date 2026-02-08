# API Contract: AI Tool Schemas

All tools are invoked by the AI agent via the OpenAI function-calling interface.
Each tool returns a standardized response: `{status, message, data}`.

## Core Tools

### create_task

```json
{
  "name": "create_task",
  "parameters": {
    "title": {"type": "string", "required": true},
    "description": {"type": "string", "required": false},
    "priority": {"type": "string", "enum": ["low","medium","high","urgent"]},
    "tags": {"type": "array", "items": {"type": "string"}},
    "due_date": {"type": "string", "format": "date-time"},
    "reminder_time": {"type": "string", "format": "date-time"}
  }
}
```

### update_task

```json
{
  "name": "update_task",
  "parameters": {
    "task_id": {"type": "string", "required": true},
    "title": {"type": "string"},
    "description": {"type": "string"},
    "priority": {"type": "string", "enum": ["low","medium","high","urgent"]},
    "tags": {"type": "array", "items": {"type": "string"}},
    "due_date": {"type": "string", "format": "date-time"}
  }
}
```

### delete_task

```json
{
  "name": "delete_task",
  "parameters": {
    "task_id": {"type": "string", "required": true},
    "confirmed": {"type": "boolean", "required": true}
  }
}
```
**Note**: AI MUST set confirmed=false first and ask user to confirm.

### complete_task

```json
{
  "name": "complete_task",
  "parameters": {
    "task_id": {"type": "string", "required": true}
  }
}
```

### list_tasks

```json
{
  "name": "list_tasks",
  "parameters": {
    "filter": {"type": "string", "enum": ["all","pending","completed"]}
  }
}
```

## Advanced Tools

### set_due_date

```json
{
  "name": "set_due_date",
  "parameters": {
    "task_id": {"type": "string", "required": true},
    "due_date": {"type": "string", "format": "date-time", "required": true}
  }
}
```

### schedule_reminder

```json
{
  "name": "schedule_reminder",
  "parameters": {
    "task_id": {"type": "string", "required": true},
    "trigger_at": {"type": "string", "format": "date-time", "required": true}
  }
}
```

### create_recurring

```json
{
  "name": "create_recurring",
  "parameters": {
    "task_id": {"type": "string", "required": true},
    "frequency": {"type": "string", "enum": ["daily","weekly","monthly","custom"], "required": true},
    "interval": {"type": "integer", "default": 1},
    "day_of_week": {"type": "integer", "min": 0, "max": 6},
    "day_of_month": {"type": "integer", "min": 1, "max": 31},
    "cron_expression": {"type": "string"}
  }
}
```

### set_priority

```json
{
  "name": "set_priority",
  "parameters": {
    "task_id": {"type": "string", "required": true},
    "priority": {"type": "string", "enum": ["low","medium","high","urgent"], "required": true}
  }
}
```

### add_tags

```json
{
  "name": "add_tags",
  "parameters": {
    "task_id": {"type": "string", "required": true},
    "tags": {"type": "array", "items": {"type": "string"}, "required": true}
  }
}
```

### search_tasks

```json
{
  "name": "search_tasks",
  "parameters": {
    "query": {"type": "string", "required": true}
  }
}
```

### filter_tasks

```json
{
  "name": "filter_tasks",
  "parameters": {
    "status": {"type": "string", "enum": ["all","pending","completed"]},
    "priority": {"type": "string", "enum": ["low","medium","high","urgent"]},
    "tags": {"type": "array", "items": {"type": "string"}},
    "due_date_from": {"type": "string", "format": "date-time"},
    "due_date_to": {"type": "string", "format": "date-time"}
  }
}
```

### sort_tasks

```json
{
  "name": "sort_tasks",
  "parameters": {
    "sort_by": {"type": "string", "enum": ["due_date","priority","created_at","updated_at"], "required": true},
    "sort_order": {"type": "string", "enum": ["asc","desc"], "default": "asc"}
  }
}
```

## Standardized Response Format

All tools return:

```json
{
  "status": "success" | "error",
  "message": "Human-readable description",
  "data": {} | [] | null
}
```
