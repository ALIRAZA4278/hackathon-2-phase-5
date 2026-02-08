"""
Task CRUD API endpoints (Phase V extended).
Per specs/api/rest-endpoints.md

Security: Every endpoint:
1. Requires JWT authentication
2. Verifies URL user_id matches JWT user_id
3. Filters queries by user_id

Phase V additions:
- T019: Query params (search, status, priority, tags, due_date range, sort)
- T020: Extended create with all new fields
- T021: Partial update for all fields
- T022: POST .../reminder (create reminder)
- T023: DELETE .../reminder (cancel reminder)
- T024: POST .../toggle (toggle completion)
- T025: Event emission on all write operations
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select
from sqlalchemy import case, String

from app.db import get_db
from app.models import Task, Reminder
from app.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    ReminderCreate,
    ReminderResponse,
)
from app.dependencies import get_current_user, verify_user_access
from app.events.producer import publish_event
from app.events.schemas import create_task_event, create_reminder_event
from app.events.topics import TODO_EVENTS, REMINDER_EVENTS

logger = logging.getLogger(__name__)

router = APIRouter(tags=["tasks"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fire_event(coro) -> None:
    """
    Fire-and-forget an async event coroutine.
    If there is a running event loop, schedule it as a task.
    Errors are logged but never propagated to the caller.
    """
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_safe_publish(coro))
    except RuntimeError:
        # No running loop -- skip event silently (e.g. in sync tests)
        logger.debug("No running event loop; skipping event emission")


async def _safe_publish(coro) -> None:
    """Await a coroutine, swallowing any exception."""
    try:
        await coro
    except Exception as exc:
        logger.warning(f"Event emission failed (non-blocking): {exc}")


def _task_payload(task: Task) -> dict:
    """Build a serialisable payload dict from a Task model instance."""
    return {
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "priority": task.priority,
        "tags": task.tags or [],
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
        "recurring_rule": task.recurring_rule,
    }


# ---------------------------------------------------------------------------
# T019: GET /{user_id}/tasks  (extended with query params)
# ---------------------------------------------------------------------------

@router.get("/{user_id}/tasks", response_model=TaskListResponse)
async def list_tasks(
    user_id: str,
    # Query parameters
    search: Optional[str] = Query(default=None, description="ILIKE search across title, description, tags"),
    status_filter: Optional[str] = Query(default=None, alias="status", description="Filter: pending/completed/all"),
    priority: Optional[str] = Query(default=None, description="Filter: low/medium/high/urgent"),
    tags: Optional[str] = Query(default=None, description="Comma-separated tag names to filter by"),
    due_date_from: Optional[datetime] = Query(default=None, description="Due date range start (ISO 8601)"),
    due_date_to: Optional[datetime] = Query(default=None, description="Due date range end (ISO 8601)"),
    sort_by: Optional[str] = Query(default=None, description="Sort field: due_date/priority/created_at/updated_at"),
    sort_order: Optional[str] = Query(default="desc", description="Sort direction: asc/desc"),
    # Auth & DB
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskListResponse:
    """
    List all tasks for the authenticated user with optional filtering and sorting.
    GET /api/{user_id}/tasks
    """
    # Security: Verify user access
    verify_user_access(user_id, current_user)

    # Base query -- always filtered by user_id
    statement = select(Task).where(Task.user_id == current_user)

    # --- Filters ---

    # Search across title, description, and tags (JSON column cast to string)
    if search:
        like_pattern = f"%{search}%"
        statement = statement.where(
            (Task.title.ilike(like_pattern))
            | (Task.description.ilike(like_pattern))
            | (Task.tags.cast(String).ilike(like_pattern))
        )

    # Status filter
    if status_filter and status_filter != "all":
        if status_filter == "completed":
            statement = statement.where(Task.completed == True)  # noqa: E712
        elif status_filter == "pending":
            statement = statement.where(Task.completed == False)  # noqa: E712

    # Priority filter
    if priority:
        statement = statement.where(Task.priority == priority)

    # Tags filter (comma-separated, match any)
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        if tag_list:
            # Build OR conditions: each tag must appear somewhere in the JSON array
            tag_conditions = [
                Task.tags.cast(String).ilike(f"%{tag}%") for tag in tag_list
            ]
            from sqlalchemy import or_ as sa_or
            statement = statement.where(sa_or(*tag_conditions))

    # Due date range
    if due_date_from:
        statement = statement.where(Task.due_date >= due_date_from)
    if due_date_to:
        statement = statement.where(Task.due_date <= due_date_to)

    # --- Sorting ---

    if sort_by == "priority":
        priority_order = case(
            (Task.priority == "low", 1),
            (Task.priority == "medium", 2),
            (Task.priority == "high", 3),
            (Task.priority == "urgent", 4),
            else_=0,
        )
        if sort_order == "asc":
            statement = statement.order_by(priority_order.asc())
        else:
            statement = statement.order_by(priority_order.desc())
    elif sort_by == "due_date":
        col = Task.due_date
        statement = statement.order_by(col.asc() if sort_order == "asc" else col.desc())
    elif sort_by == "updated_at":
        col = Task.updated_at
        statement = statement.order_by(col.asc() if sort_order == "asc" else col.desc())
    elif sort_by == "created_at":
        col = Task.created_at
        statement = statement.order_by(col.asc() if sort_order == "asc" else col.desc())
    else:
        # Default sort: newest first
        statement = statement.order_by(Task.created_at.desc())

    tasks = db.exec(statement).all()
    return TaskListResponse(tasks=tasks, count=len(tasks))


# ---------------------------------------------------------------------------
# T020: POST /{user_id}/tasks  (extended create with all new fields)
# ---------------------------------------------------------------------------

@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskResponse:
    """
    Create a new task for the authenticated user.
    POST /api/{user_id}/tasks
    """
    # Security: Verify user access
    verify_user_access(user_id, current_user)

    now = datetime.now(timezone.utc)
    task = Task(
        user_id=current_user,
        title=task_data.title,
        description=task_data.description,
        completed=False,
        priority=task_data.priority or "medium",
        tags=task_data.tags or [],
        due_date=task_data.due_date,
        reminder_time=task_data.reminder_time,
        recurring_rule=task_data.recurring_rule,
        created_at=now,
        updated_at=now,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    # T025: Emit task_created event (fire-and-forget)
    event = create_task_event(
        event_type="task_created",
        entity_id=str(task.id),
        user_id=current_user,
        payload=_task_payload(task),
    )
    _fire_event(publish_event(TODO_EVENTS, event))

    return task


# ---------------------------------------------------------------------------
# GET /{user_id}/tasks/{task_id}  (unchanged from Phase II)
# ---------------------------------------------------------------------------

@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    task_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskResponse:
    """
    Get a specific task by ID.
    GET /api/{user_id}/tasks/{task_id}
    """
    verify_user_access(user_id, current_user)

    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user)
    task = db.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


# ---------------------------------------------------------------------------
# T021: PUT /{user_id}/tasks/{task_id}  (extended partial update)
# ---------------------------------------------------------------------------

@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskResponse:
    """
    Update a task (partial -- only provided fields are changed).
    PUT /api/{user_id}/tasks/{task_id}
    """
    verify_user_access(user_id, current_user)

    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user)
    task = db.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Only update fields that are explicitly provided (not None)
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    task.updated_at = datetime.now(timezone.utc)

    db.add(task)
    db.commit()
    db.refresh(task)

    # T025: Emit task_updated event (fire-and-forget)
    event = create_task_event(
        event_type="task_updated",
        entity_id=str(task.id),
        user_id=current_user,
        payload=_task_payload(task),
    )
    _fire_event(publish_event(TODO_EVENTS, event))

    return task


# ---------------------------------------------------------------------------
# DELETE /{user_id}/tasks/{task_id}  (with event emission)
# ---------------------------------------------------------------------------

@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a task permanently.
    DELETE /api/{user_id}/tasks/{task_id}
    """
    verify_user_access(user_id, current_user)

    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user)
    task = db.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Capture info before deletion for the event
    deleted_id = str(task.id)
    deleted_payload = _task_payload(task)

    db.delete(task)
    db.commit()

    # T025: Emit task_deleted event (fire-and-forget)
    event = create_task_event(
        event_type="task_deleted",
        entity_id=deleted_id,
        user_id=current_user,
        payload=deleted_payload,
    )
    _fire_event(publish_event(TODO_EVENTS, event))


# ---------------------------------------------------------------------------
# PATCH /{user_id}/tasks/{task_id}/complete  (backward compat)
# ---------------------------------------------------------------------------

@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    user_id: str,
    task_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskResponse:
    """
    Toggle task completion status (legacy endpoint, kept for backward compat).
    PATCH /api/{user_id}/tasks/{task_id}/complete
    """
    return await _toggle_task(user_id, task_id, current_user, db)


# ---------------------------------------------------------------------------
# T024: POST /{user_id}/tasks/{task_id}/toggle  (new API contract)
# ---------------------------------------------------------------------------

@router.post("/{user_id}/tasks/{task_id}/toggle", response_model=TaskResponse)
async def toggle_task(
    user_id: str,
    task_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskResponse:
    """
    Toggle task completion status.
    POST /api/{user_id}/tasks/{task_id}/toggle
    """
    return await _toggle_task(user_id, task_id, current_user, db)


async def _toggle_task(
    user_id: str,
    task_id: int,
    current_user: str,
    db: Session,
) -> TaskResponse:
    """Shared implementation for both toggle endpoints."""
    verify_user_access(user_id, current_user)

    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user)
    task = db.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    task.completed = not task.completed
    task.updated_at = datetime.now(timezone.utc)

    db.add(task)
    db.commit()
    db.refresh(task)

    # T025: Emit task_completed event (fire-and-forget)
    event = create_task_event(
        event_type="task_completed",
        entity_id=str(task.id),
        user_id=current_user,
        payload={**_task_payload(task), "completed": task.completed},
    )
    _fire_event(publish_event(TODO_EVENTS, event))

    return task


# ---------------------------------------------------------------------------
# T022: POST /{user_id}/tasks/{task_id}/reminder  (create reminder)
# ---------------------------------------------------------------------------

@router.post(
    "/{user_id}/tasks/{task_id}/reminder",
    response_model=ReminderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_reminder(
    user_id: str,
    task_id: int,
    reminder_data: ReminderCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReminderResponse:
    """
    Create a reminder for a task.
    POST /api/{user_id}/tasks/{task_id}/reminder
    """
    verify_user_access(user_id, current_user)

    # Verify the task exists and belongs to this user
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user)
    task = db.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Create the reminder
    reminder = Reminder(
        task_id=task_id,
        user_id=current_user,
        trigger_at=reminder_data.trigger_at,
        status="pending",
        created_at=datetime.now(timezone.utc),
    )

    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    # Emit reminder_scheduled event (fire-and-forget)
    event = create_reminder_event(
        event_type="reminder_scheduled",
        entity_id=str(reminder.id),
        user_id=current_user,
        payload={
            "task_id": task_id,
            "trigger_at": reminder.trigger_at.isoformat(),
        },
    )
    _fire_event(publish_event(REMINDER_EVENTS, event))

    return reminder


# ---------------------------------------------------------------------------
# T023: DELETE /{user_id}/tasks/{task_id}/reminder  (cancel reminder)
# ---------------------------------------------------------------------------

@router.delete("/{user_id}/tasks/{task_id}/reminder")
async def cancel_reminder(
    user_id: str,
    task_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cancel the pending reminder for a task.
    DELETE /api/{user_id}/tasks/{task_id}/reminder
    """
    verify_user_access(user_id, current_user)

    # Find pending reminder for this task + user
    statement = select(Reminder).where(
        Reminder.task_id == task_id,
        Reminder.user_id == current_user,
        Reminder.status == "pending",
    )
    reminder = db.exec(statement).first()

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending reminder found for this task",
        )

    reminder.status = "cancelled"

    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    # Emit reminder_cancelled event (fire-and-forget)
    event = create_reminder_event(
        event_type="reminder_cancelled",
        entity_id=str(reminder.id),
        user_id=current_user,
        payload={
            "task_id": task_id,
            "trigger_at": reminder.trigger_at.isoformat(),
        },
    )
    _fire_event(publish_event(REMINDER_EVENTS, event))

    return {"detail": "Reminder cancelled successfully"}
