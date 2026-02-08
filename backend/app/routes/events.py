"""
Dapr pub/sub subscription and event handler endpoints.

These endpoints enable the backend to receive events from Dapr pub/sub.
- GET /dapr/subscribe: Dapr calls this to discover subscriptions
- POST /events/{topic}: Dapr delivers CloudEvents to these handlers

Per specs/002-cloud-native-platform/contracts/events-api.md
"""
import logging
import json
from typing import Any, Dict, List
from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)

router = APIRouter(tags=["events"])


# ---------------------------------------------------------------------------
# Dapr subscription discovery endpoint
# Dapr sidecar calls GET /dapr/subscribe on startup to learn which
# topics this app subscribes to and where to route them.
# ---------------------------------------------------------------------------

@router.get("/dapr/subscribe")
async def dapr_subscribe() -> List[Dict[str, str]]:
    """
    Return Dapr subscription list.
    Dapr sidecar calls this endpoint at startup to register subscriptions.
    """
    subscriptions = [
        {
            "pubsubname": "pubsub",
            "topic": "todo.events",
            "route": "/events/todo",
        },
        {
            "pubsubname": "pubsub",
            "topic": "reminder.events",
            "route": "/events/reminder",
        },
        {
            "pubsubname": "pubsub",
            "topic": "recurring.events",
            "route": "/events/recurring",
        },
    ]
    logger.info("Dapr subscription discovery: returning %d subscriptions", len(subscriptions))
    return subscriptions


# ---------------------------------------------------------------------------
# Event handlers
# All handlers MUST return {"status": "SUCCESS"} for Dapr to ACK the message.
# Returning any other status (or an error) causes Dapr to retry delivery.
# ---------------------------------------------------------------------------

@router.post("/events/todo")
async def handle_todo_event(request: Request) -> Dict[str, str]:
    """
    Handle CloudEvents delivered to the todo.events topic.
    Logs the event for observability; business logic delegated to consumers.
    """
    try:
        body = await request.json()
        event_data = body.get("data", body)
        logger.info(
            "Received todo event: type=%s entity=%s user=%s",
            event_data.get("event_type", "unknown"),
            event_data.get("entity_id", "unknown"),
            event_data.get("user_id", "unknown"),
        )
    except Exception as exc:
        logger.error("Failed to parse todo event: %s", exc)

    return {"status": "SUCCESS"}


@router.post("/events/reminder")
async def handle_reminder_event(request: Request) -> Dict[str, str]:
    """
    Handle CloudEvents delivered to the reminder.events topic.
    """
    try:
        body = await request.json()
        event_data = body.get("data", body)
        logger.info(
            "Received reminder event: type=%s entity=%s user=%s",
            event_data.get("event_type", "unknown"),
            event_data.get("entity_id", "unknown"),
            event_data.get("user_id", "unknown"),
        )
    except Exception as exc:
        logger.error("Failed to parse reminder event: %s", exc)

    return {"status": "SUCCESS"}


@router.post("/events/recurring")
async def handle_recurring_event(request: Request) -> Dict[str, str]:
    """
    Handle CloudEvents delivered to the recurring.events topic.
    """
    try:
        body = await request.json()
        event_data = body.get("data", body)
        logger.info(
            "Received recurring event: type=%s entity=%s user=%s",
            event_data.get("event_type", "unknown"),
            event_data.get("entity_id", "unknown"),
            event_data.get("user_id", "unknown"),
        )
    except Exception as exc:
        logger.error("Failed to parse recurring event: %s", exc)

    return {"status": "SUCCESS"}
