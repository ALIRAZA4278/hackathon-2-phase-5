"""
Notification Consumer Service

Standalone FastAPI microservice that subscribes to Dapr pub/sub topic
(todo.events) and processes events as notifications.

Currently a placeholder for real notification delivery (email, push, etc.).
Includes idempotency tracking to prevent duplicate processing.

Per specs/002-cloud-native-platform — Phase V cloud-native platform.
"""
import logging
import json
import sys
from typing import Any, Dict, List, Set

from fastapi import FastAPI, Request
from pydantic_settings import BaseSettings

# ---------------------------------------------------------------------------
# Structured JSON logging
# ---------------------------------------------------------------------------
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter(
        json.dumps({
            "timestamp": "%(asctime)s",
            "level": "%(levelname)s",
            "service": "notification-consumer",
            "message": "%(message)s",
        })
    )
)
logger = logging.getLogger("notification-consumer")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# ---------------------------------------------------------------------------
# Configuration (pydantic-settings)
# ---------------------------------------------------------------------------

class Settings(BaseSettings):
    """Consumer configuration loaded from environment."""
    service_name: str = "notification-consumer"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()

# ---------------------------------------------------------------------------
# Idempotency tracking (T065)
# In-memory set of processed event IDs to prevent duplicate notifications.
# ---------------------------------------------------------------------------
_processed_keys: Set[str] = set()

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(title="Notification Consumer", version="1.0.0")


@app.get("/dapr/subscribe")
async def dapr_subscribe() -> List[Dict[str, str]]:
    """Return Dapr subscription list for the notification consumer."""
    return [
        {"pubsubname": "pubsub", "topic": "todo.events", "route": "/events/todo"},
    ]


def _extract_event_data(body: dict) -> dict:
    """Extract event data from CloudEvent envelope or raw payload."""
    return body.get("data", body)


def _is_duplicate(idempotency_key: str) -> bool:
    """Check if an event has already been processed."""
    if idempotency_key in _processed_keys:
        logger.info("Duplicate notification skipped: key=%s", idempotency_key)
        return True
    return False


def _mark_processed(idempotency_key: str) -> None:
    """Record that an event has been processed."""
    _processed_keys.add(idempotency_key)


def _send_notification(event_data: dict) -> None:
    """
    Placeholder for real notification delivery.

    In a production system this would:
    - Send push notifications via Firebase/APNs
    - Send email via SendGrid/SES
    - Send SMS via Twilio
    - Post to Slack/Teams webhooks

    Currently logs the notification for observability.
    """
    event_type = event_data.get("event_type", "unknown")
    entity_id = event_data.get("entity_id", "unknown")
    user_id = event_data.get("user_id", "unknown")
    payload = event_data.get("payload", {})

    logger.info(
        "NOTIFICATION [%s]: entity=%s user=%s payload_keys=%s",
        event_type,
        entity_id,
        user_id,
        list(payload.keys()) if isinstance(payload, dict) else "N/A",
    )


@app.post("/events/todo")
async def handle_todo_event(request: Request) -> Dict[str, str]:
    """Handle todo.events and dispatch notifications."""
    try:
        body = await request.json()
        event_data = _extract_event_data(body)
        idempotency_key = event_data.get("idempotency_key", "")

        if idempotency_key and _is_duplicate(idempotency_key):
            return {"status": "SUCCESS"}

        logger.info(
            "Notification todo event: type=%s entity=%s user=%s",
            event_data.get("event_type"),
            event_data.get("entity_id"),
            event_data.get("user_id"),
        )

        _send_notification(event_data)

        if idempotency_key:
            _mark_processed(idempotency_key)
    except Exception as exc:
        logger.error("Error handling todo event for notification: %s", exc)

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
        "status": "ok",
    }
