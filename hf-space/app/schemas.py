"""
Pydantic schemas for request/response validation.
Per specs/api/rest-endpoints.md and specs/001-ai-chatbot/contracts/chat-api.yaml
"""
from datetime import datetime
from typing import Optional, List
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
    """Schema for creating a new task."""
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title (1-200 characters)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Task description (max 1000 characters)"
    )


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title (1-200 characters)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Task description (max 1000 characters)"
    )


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for list of tasks response."""
    tasks: List[TaskResponse]
    count: int
