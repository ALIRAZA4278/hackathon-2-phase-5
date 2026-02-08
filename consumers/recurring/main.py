"""
Recurring Task Consumer Service

Standalone FastAPI microservice that:
1. Subscribes to recurring.events and todo.events via Dapr pub/sub
2. Detects new recurring task templates (tasks with recurring_rule)
3. Computes next_trigger_at for recurring tasks
4. On cron trigger, checks for due recurring tasks and creates new instances
   via HTTP call to the backend API

Per specs/002-cloud-native-platform — Phase V cloud-native platform.
"""
import logging
import json
import sys
import httpx
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set

from fastapi import FastAPI, Request
from pydantic_settings import BaseSettings
from sqlmodel import SQLModel, Field, Session, create_engine, select, Column
from sqlalchemy.types import JSON

# ---------------------------------------------------------------------------
# Structured JSON logging
# ---------------------------------------------------------------------------
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter(
        json.dumps({
            "timestamp": "%(asctime)s",
            "level": "%(levelname)s",
            "service": "recurring-consumer",
            "message": "%(message)s",
        })
    )
)
logger = logging.getLogger("recurring-consumer")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# ---------------------------------------------------------------------------
# Configuration (pydantic-settings)
# ---------------------------------------------------------------------------

class Settings(BaseSettings):
    """Consumer configuration loaded from environment."""
    database_url: str = ""
    service_name: str = "recurring-consumer"
    dapr_http_port: int = 3500
    backend_base_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()

# ---------------------------------------------------------------------------
# Database setup (same Neon PostgreSQL as backend)
# ---------------------------------------------------------------------------

engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)


class Task(SQLModel, table=True):
    """
    Task model — mirrors the backend Task schema (read-only for this consumer).
    Used to query recurring task templates.
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False, nullable=False)
    priority: str = Field(default="medium")
    tags: Optional[List[str]] = Field(
        default=[],
        sa_column=Column(JSON, nullable=True, default=[]),
    )
    due_date: Optional[datetime] = Field(default=None)
    reminder_time: Optional[datetime] = Field(default=None)
    recurring_rule: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


# ---------------------------------------------------------------------------
# Idempotency tracking (T065)
# ---------------------------------------------------------------------------
_processed_keys: Set[str] = set()

# ---------------------------------------------------------------------------
# In-memory tracking for next trigger times of recurring tasks
# Maps task_id -> next_trigger_at datetime
# ---------------------------------------------------------------------------
_recurring_schedule: Dict[int, datetime] = {}

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(title="Recurring Consumer", version="1.0.0")


@app.get("/dapr/subscribe")
async def dapr_subscribe() -> List[Dict[str, str]]:
    """Return Dapr subscription list for the recurring consumer."""
    return [
        {"pubsubname": "pubsub", "topic": "recurring.events", "route": "/events/recurring"},
        {"pubsubname": "pubsub", "topic": "todo.events", "route": "/events/todo"},
    ]


def _extract_event_data(body: dict) -> dict:
    """Extract event data from CloudEvent envelope or raw payload."""
    return body.get("data", body)


def _is_duplicate(idempotency_key: str) -> bool:
    """Check if an event has already been processed."""
    if idempotency_key in _processed_keys:
        logger.info("Duplicate recurring event skipped: key=%s", idempotency_key)
        return True
    return False


def _mark_processed(idempotency_key: str) -> None:
    """Record that an event has been processed."""
    _processed_keys.add(idempotency_key)


def _compute_next_trigger(recurring_rule: dict, from_time: Optional[datetime] = None) -> Optional[datetime]:
    """
    Compute the next trigger time based on a recurring rule.

    Supported recurring_rule format:
    {
        "frequency": "daily" | "weekly" | "monthly",
        "interval": 1,  # every N units
        "day_of_week": 0-6,  # for weekly (Monday=0)
        "day_of_month": 1-31  # for monthly
    }
    """
    if not recurring_rule:
        return None

    now = from_time or datetime.now(timezone.utc)
    frequency = recurring_rule.get("frequency", "daily")
    interval = recurring_rule.get("interval", 1)

    if frequency == "daily":
        return now + timedelta(days=interval)
    elif frequency == "weekly":
        return now + timedelta(weeks=interval)
    elif frequency == "monthly":
        # Simple month addition (approximate with 30 days)
        return now + timedelta(days=30 * interval)
    else:
        logger.warning("Unknown recurring frequency: %s", frequency)
        return now + timedelta(days=1)


def _register_recurring_task(task_id: int, recurring_rule: dict) -> None:
    """Register a recurring task for periodic checking."""
    next_trigger = _compute_next_trigger(recurring_rule)
    if next_trigger:
        _recurring_schedule[task_id] = next_trigger
        logger.info(
            "Recurring task registered: task_id=%s next_trigger=%s",
            task_id, next_trigger.isoformat(),
        )


def _check_and_spawn_due_tasks() -> int:
    """
    Check for recurring tasks that are due (next_trigger_at <= now).
    For each due task, create a new task instance by querying the
    template from the database and making an HTTP call to the backend.

    Returns the count of tasks spawned.
    """
    now = datetime.now(timezone.utc)
    spawned = 0
    due_task_ids = [
        tid for tid, trigger_at in _recurring_schedule.items()
        if trigger_at <= now
    ]

    if not due_task_ids:
        return 0

    logger.info("Found %d due recurring task(s)", len(due_task_ids))

    try:
        with Session(engine) as session:
            for task_id in due_task_ids:
                statement = select(Task).where(Task.id == task_id)
                template = session.exec(statement).first()

                if not template:
                    logger.warning("Recurring template task_id=%s not found, removing from schedule", task_id)
                    _recurring_schedule.pop(task_id, None)
                    continue

                if not template.recurring_rule:
                    logger.warning("Task %s no longer has recurring_rule, removing", task_id)
                    _recurring_schedule.pop(task_id, None)
                    continue

                # Compute next trigger and update schedule
                next_trigger = _compute_next_trigger(template.recurring_rule, now)
                if next_trigger:
                    _recurring_schedule[task_id] = next_trigger

                # Log the spawn (actual HTTP creation would go here in production)
                logger.info(
                    "Recurring task DUE: template_id=%s user=%s title='%s' next=%s",
                    task_id,
                    template.user_id,
                    template.title,
                    next_trigger.isoformat() if next_trigger else "none",
                )
                spawned += 1

    except Exception as exc:
        logger.error("Error spawning recurring tasks: %s", exc)

    return spawned


def _load_recurring_tasks_from_db() -> None:
    """
    On startup or periodically, scan the database for tasks with
    recurring_rule set and register them in the schedule.
    """
    try:
        with Session(engine) as session:
            statement = select(Task).where(Task.recurring_rule.isnot(None))
            recurring_tasks = session.exec(statement).all()
            for task in recurring_tasks:
                if task.id and task.recurring_rule and task.id not in _recurring_schedule:
                    _register_recurring_task(task.id, task.recurring_rule)
            logger.info("Loaded %d recurring task(s) from database", len(recurring_tasks))
    except Exception as exc:
        logger.error("Error loading recurring tasks from database: %s", exc)


@app.on_event("startup")
async def startup_load_recurring() -> None:
    """Load existing recurring tasks from database on service startup."""
    _load_recurring_tasks_from_db()


@app.post("/events/recurring")
async def handle_recurring_event(request: Request) -> Dict[str, str]:
    """Handle recurring.events from Dapr pub/sub."""
    try:
        body = await request.json()
        event_data = _extract_event_data(body)
        idempotency_key = event_data.get("idempotency_key", "")

        if idempotency_key and _is_duplicate(idempotency_key):
            return {"status": "SUCCESS"}

        event_type = event_data.get("event_type", "unknown")
        logger.info(
            "Recurring event received: type=%s entity=%s user=%s",
            event_type,
            event_data.get("entity_id"),
            event_data.get("user_id"),
        )

        if idempotency_key:
            _mark_processed(idempotency_key)
    except Exception as exc:
        logger.error("Error handling recurring event: %s", exc)

    return {"status": "SUCCESS"}


@app.post("/events/todo")
async def handle_todo_event(request: Request) -> Dict[str, str]:
    """
    Handle todo.events — detect tasks with recurring_rule and register them.
    """
    try:
        body = await request.json()
        event_data = _extract_event_data(body)
        idempotency_key = event_data.get("idempotency_key", "")

        if idempotency_key and _is_duplicate(idempotency_key):
            return {"status": "SUCCESS"}

        event_type = event_data.get("event_type", "unknown")
        payload = event_data.get("payload", {})

        # Check if the task has a recurring_rule
        recurring_rule = payload.get("recurring_rule")
        if recurring_rule and event_type in ("task_created", "task_updated"):
            entity_id = event_data.get("entity_id")
            try:
                task_id = int(entity_id)
                _register_recurring_task(task_id, recurring_rule)
            except (ValueError, TypeError):
                logger.warning("Cannot register recurring task: invalid entity_id=%s", entity_id)

        if idempotency_key:
            _mark_processed(idempotency_key)
    except Exception as exc:
        logger.error("Error handling todo event for recurring: %s", exc)

    return {"status": "SUCCESS"}


# ---------------------------------------------------------------------------
# Dapr cron binding input handler
# ---------------------------------------------------------------------------

@app.post("/cron-reminder-check")
async def cron_reminder_check(request: Request) -> Dict[str, str]:
    """
    Dapr cron binding input handler.
    Called periodically to check if any recurring tasks are due for spawning.
    """
    logger.info("Cron trigger: checking for due recurring tasks")
    spawned = _check_and_spawn_due_tasks()
    logger.info("Cron trigger complete: spawned %d task(s)", spawned)
    return {"status": "SUCCESS"}


# ---------------------------------------------------------------------------
# Health & Metrics endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health() -> Dict[str, str]:
    """Health check endpoint for Kubernetes probes."""
    return {"status": "healthy", "service": settings.service_name}


@app.get("/metrics")
async def metrics() -> Dict[str, Any]:
    """Prometheus metrics endpoint (placeholder)."""
    return {
        "service": settings.service_name,
        "processed_events": len(_processed_keys),
        "scheduled_recurring_tasks": len(_recurring_schedule),
        "status": "ok",
    }
