"""
Pydantic schemas for request/response validation.
Per specs/api/rest-endpoints.md, specs/001-ai-chatbot/contracts/chat-api.yaml,
and specs/002-cloud-native-platform/contracts/ (Phase V)
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# Chat Schemas (Phase III AI Chatbot)
# ============================================================================

class ChatRequest(BaseModel):
    """Request body for POST /api/{user_id}/chat endpoint."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's natural language message"
    )
    conversation_id: Optional[int] = Field(
        default=None,
        description="Existing conversation ID (optional, creates new if omitted)"
    )


class MessageResponse(BaseModel):
    """Single message in a chat response."""
    id: int = Field(..., description="Message ID")
    role: str = Field(..., description="Message author: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    created_at: str = Field(..., description="Message timestamp (UTC, ISO 8601)")


class ChatResponse(BaseModel):
    """Response body for POST /api/{user_id}/chat endpoint."""
    conversation_id: int = Field(..., description="The conversation ID")
    message: MessageResponse = Field(..., description="The assistant's response message")


class ConversationResponse(BaseModel):
    """Single conversation in list response."""
    id: int = Field(..., description="Conversation ID")
    created_at: str = Field(..., description="Conversation creation timestamp (UTC, ISO 8601)")
    updated_at: str = Field(..., description="Last update timestamp (UTC, ISO 8601)")


class ConversationListResponse(BaseModel):
    """Response body for GET /api/{user_id}/conversations endpoint."""
    conversations: List[ConversationResponse] = Field(
        ...,
        description="List of user's conversations"
    )


class MessageListResponse(BaseModel):
    """Response body for GET /api/{user_id}/conversations/{id}/messages endpoint."""
    messages: List[MessageResponse] = Field(
        ...,
        description="List of messages in the conversation"
    )


# ============================================================================
# Task Schemas
# ============================================================================

class TaskCreate(BaseModel):
    """Schema for creating a new task with optional advanced attributes."""
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title (1-200 characters)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Task description (max 2000 characters)"
    )
    priority: Optional[str] = Field(
        default="medium",
        description="Priority: low, medium, high, urgent"
    )
    tags: Optional[List[str]] = Field(
        default=[],
        description="List of tag strings"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Due date (ISO 8601)"
    )
    reminder_time: Optional[datetime] = Field(
        default=None,
        description="Reminder trigger time"
    )
    recurring_rule: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Recurrence configuration"
    )


class TaskUpdate(BaseModel):
    """Schema for partial updates to an existing task."""
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Task title (1-200 characters)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Task description (max 2000 characters)"
    )
    completed: Optional[bool] = Field(
        default=None,
        description="Task completion status"
    )
    priority: Optional[str] = Field(
        default=None,
        description="Priority: low, medium, high, urgent"
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="List of tag strings"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Due date (ISO 8601)"
    )
    reminder_time: Optional[datetime] = Field(
        default=None,
        description="Reminder trigger time"
    )
    recurring_rule: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Recurrence configuration"
    )


class TaskResponse(BaseModel):
    """Schema for task response with Phase V advanced attributes."""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    priority: str = "medium"
    tags: Optional[List[str]] = []
    due_date: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    recurring_rule: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for list of tasks response."""
    tasks: List[TaskResponse]
    count: int


# ============================================================================
# Phase V: Reminder & AuditLog Schemas
# ============================================================================

class ReminderCreate(BaseModel):
    """Schema for setting a reminder."""
    trigger_at: datetime = Field(
        ...,
        description="When to fire the reminder (ISO 8601)"
    )


class ReminderResponse(BaseModel):
    """Schema for reminder response."""
    id: int
    task_id: int
    user_id: str
    trigger_at: datetime
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    """Schema for audit log response."""
    id: int
    action: str
    entity_type: str
    entity_id: str
    user_id: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
