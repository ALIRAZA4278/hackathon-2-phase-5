"""
SQLModel database models.
Per specs/database/schema.md and specs/001-ai-chatbot/data-model.md
"""
from datetime import datetime, timezone
from typing import Optional, Literal
from sqlmodel import SQLModel, Field


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
# Task Models (Phase II)
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
