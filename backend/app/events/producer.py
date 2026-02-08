"""
Dapr pub/sub event publisher.
Publishes events via Dapr sidecar HTTP API.
Per specs/002-cloud-native-platform/contracts/events-api.md

Constitution: No direct Kafka client in application code.
All event publishing goes through Dapr HTTP API.
"""
import httpx
import json
import logging
from typing import Dict, Any
from app.config import get_settings
from app.events.topics import PUBSUB_NAME

logger = logging.getLogger(__name__)


async def publish_event(topic: str, event_data: Dict[str, Any]) -> bool:
    """
    Publish an event to a Dapr pub/sub topic.

    Args:
        topic: Topic name (e.g., "todo.events")
        event_data: Event payload dict (from event schema helpers)

    Returns:
        True if published successfully, False otherwise.
    """
    settings = get_settings()
    dapr_url = f"http://localhost:{settings.dapr_http_port}/v1.0/publish/{PUBSUB_NAME}/{topic}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                dapr_url,
                json=event_data,
                headers={"Content-Type": "application/json"},
                timeout=5.0
            )

            if response.status_code in (200, 204):
                logger.info(
                    f"Event published: {event_data.get('event_type')} "
                    f"to {topic} (entity: {event_data.get('entity_id')})"
                )
                return True
            else:
                logger.warning(
                    f"Event publish failed: {topic} "
                    f"status={response.status_code} body={response.text}"
                )
                return False

    except httpx.ConnectError:
        # Dapr sidecar not available (local dev without Dapr)
        logger.debug(
            f"Dapr sidecar not available, skipping event: "
            f"{event_data.get('event_type')} to {topic}"
        )
        return False
    except Exception as e:
        logger.error(f"Event publish error: {topic} - {e}")
        return False
