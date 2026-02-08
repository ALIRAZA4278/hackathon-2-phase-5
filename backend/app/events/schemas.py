"""
Event payload schemas for Phase V cloud-native platform.
Per specs/002-cloud-native-platform/contracts/events-api.md
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    """Base event payload schema. All events extend this."""
    event_type: str = Field(..., description="Event identifier")
    entity_id: str = Field(..., description="Affected entity ID")
    user_id: str = Field(..., description="Owning user")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Event time (ISO 8601)"
    )
    idempotency_key: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Dedup key"
    )
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific data"
    )


class TaskEvent(BaseEvent):
    """Event for task lifecycle operations (create, update, delete, complete)."""
    pass


class ReminderEvent(BaseEvent):
    """Event for reminder operations (scheduled, triggered, cancelled)."""
    pass


class RecurringEvent(BaseEvent):
    """Event for recurring task spawning."""
    pass


class AuditEvent(BaseEvent):
    """Event for audit trail entries."""
    pass


class AIToolEvent(BaseEvent):
    """Event for AI tool invocations."""
    pass


def create_task_event(
    event_type: str,
    entity_id: str,
    user_id: str,
    payload: Dict[str, Any]
) -> dict:
    """Helper to create a task event dict ready for publishing."""
    event = TaskEvent(
        event_type=event_type,
        entity_id=str(entity_id),
        user_id=user_id,
        payload=payload
    )
    return event.model_dump(mode="json")


def create_reminder_event(
    event_type: str,
    entity_id: str,
    user_id: str,
    payload: Dict[str, Any]
) -> dict:
    """Helper to create a reminder event dict."""
    event = ReminderEvent(
        event_type=event_type,
        entity_id=str(entity_id),
        user_id=user_id,
        payload=payload
    )
    return event.model_dump(mode="json")


def create_ai_tool_event(
    entity_id: str,
    user_id: str,
    tool_name: str,
    arguments: Dict[str, Any],
    result_status: str,
    duration_ms: int
) -> dict:
    """Helper to create an AI tool event dict."""
    event = AIToolEvent(
        event_type="ai_tool_called",
        entity_id=str(entity_id) if entity_id else "none",
        user_id=user_id,
        payload={
            "tool_name": tool_name,
            "arguments": arguments,
            "result_status": result_status,
            "duration_ms": duration_ms
        }
    )
    return event.model_dump(mode="json")
