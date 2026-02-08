# API Contract: Chat (AI Chatbot)

**Base Path**: `/api/{user_id}/chat`
**Auth**: JWT Bearer token required on all endpoints

## Endpoints

### POST /api/{user_id}/chat

Send a message to the AI chatbot.

**Request Body**:
```json
{
  "message": "Create a task called Buy groceries with high priority",
  "conversation_id": "uuid (optional, creates new if omitted)"
}
```

**Response** (200):
```json
{
  "response": "I've created a new task 'Buy groceries' with high priority.",
  "conversation_id": "uuid",
  "tool_calls": [
    {
      "tool": "create_task",
      "arguments": {"title": "Buy groceries", "priority": "high"},
      "result": {"status": "success", "data": {"id": "uuid", "title": "Buy groceries"}}
    }
  ]
}
```

**Rate Limit**: 200 requests/minute per user
**Events emitted**: `ai_tool_called` on `ai.events` (for each tool call)

### GET /api/{user_id}/conversations

List user's conversations.

**Response** (200):
```json
{
  "conversations": [
    {
      "id": "uuid",
      "created_at": "2026-02-07T10:00:00Z",
      "updated_at": "2026-02-07T10:30:00Z"
    }
  ]
}
```

### GET /api/{user_id}/conversations/{conversation_id}/messages

Get messages for a conversation.

**Response** (200):
```json
{
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "content": "Show my tasks",
      "created_at": "2026-02-07T10:00:00Z"
    },
    {
      "id": "uuid",
      "role": "assistant",
      "content": "Here are your tasks...",
      "created_at": "2026-02-07T10:00:01Z"
    }
  ]
}
```

## Error Responses

| Status | Description |
|--------|-------------|
| 400 | Empty or invalid message |
| 401 | Missing or invalid JWT |
| 403 | User ID mismatch |
| 429 | Rate limit exceeded (200 req/min) |
| 500 | AI model error (fallback response returned) |
