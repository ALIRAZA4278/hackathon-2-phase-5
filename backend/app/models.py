"""
SQLModel database models.
Per specs/database/schema.md, specs/001-ai-chatbot/data-model.md,
and specs/002-cloud-native-platform/data-model.md (Phase V)
"""
from datetime import datetime, timezone
from typing import Optional, List, Literal
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.types import JSON


# ============================================================================
# Chat Models (Phase III AI Chatbot)
# ============================================================================

class Conversation(SQLModel, table=True):
    """
    Conversation model representing a chat session between user and AI.

    Each conversation contains multiple messages and belongs to a single user.
    Conversations are persisted to allow resumption across page refreshes.
    """
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(
        index=True,
        nullable=False,
        description="Foreign key to users.id (Better Auth managed)"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Conversation creation timestamp (UTC)"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Last activity timestamp (UTC)"
    )


class Message(SQLModel, table=True):
    """
    Message model representing a single message in a conversation.

    Messages can be from either the user or the AI assistant.
    All messages are persisted for conversation continuity.
    """
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(
        index=True,
        nullable=False,
        description="Foreign key to users.id (for user isolation)"
    )
    conversation_id: int = Field(
        index=True,
        nullable=False,
        foreign_key="conversations.id",
        description="Foreign key to conversations.id"
    )
    role: str = Field(
        nullable=False,
        description="Message author: 'user' or 'assistant'"
    )
    content: str = Field(
        nullable=False,
        description="Message content"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Message timestamp (UTC)"
    )


# ============================================================================
# Phase V: Reminder Model
# ============================================================================

class Reminder(SQLModel, table=True):
    """
    Reminder model for scheduled task notifications.
    State transitions: pending → triggered (on fire) or pending → cancelled (on delete)
    """
    __tablename__ = "reminders"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(
        index=True,
        nullable=False,
        description="Related task ID"
    )
    user_id: str = Field(
        index=True,
        nullable=False,
        description="Owner (from JWT)"
    )
    trigger_at: datetime = Field(
        nullable=False,
        description="When to fire the reminder"
    )
    status: str = Field(
        default="pending",
        nullable=False,
        description="Reminder status: pending, triggered, cancelled"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Creation timestamp (UTC)"
    )


# ============================================================================
# Phase V: AuditLog Model
# ============================================================================

class AuditLog(SQLModel, table=True):
    """
    Immutable audit log record for system operations.
    """
    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    action: str = Field(
        nullable=False,
        description="Operation performed (e.g., task_created)"
    )
    entity_type: str = Field(
        nullable=False,
        description="Entity affected (e.g., task, reminder)"
    )
    entity_id: str = Field(
        nullable=False,
        description="ID of affected entity"
    )
    user_id: str = Field(
        index=True,
        nullable=False,
        description="Who performed the action"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="When the action occurred"
    )
    details: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
        description="Additional context"
    )


# ============================================================================
# Task Models (Phase II + Phase V extensions)
# ============================================================================

class Task(SQLModel, table=True):
    """
    Task model representing a user's todo item.

    Security: Every task belongs to a user and can only be
    accessed by that user (enforced at API level).
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(
        index=True,
        nullable=False,
        description="Foreign key to users.id (Better Auth managed)"
    )
    title: str = Field(
        min_length=1,
        max_length=200,
        nullable=False,
        description="Task title (1-200 characters)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Task description (max 1000 characters)"
    )
    completed: bool = Field(
        default=False,
        nullable=False,
        description="Task completion status"
    )
    # Phase V: Advanced task attributes
    priority: str = Field(
        default="medium",
        description="Priority level: low, medium, high, urgent"
    )
    tags: Optional[List[str]] = Field(
        default=[],
        sa_column=Column(JSON, nullable=True, default=[]),
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
    recurring_rule: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
        description="Recurrence configuration JSON"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Task creation timestamp (UTC)"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Last update timestamp (UTC)"
    )
