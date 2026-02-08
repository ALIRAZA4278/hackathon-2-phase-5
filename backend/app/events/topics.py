"""
Topic name constants for Dapr pub/sub.
Per specs/002-cloud-native-platform/contracts/events-api.md
"""

# Pub/sub component name (must match dapr/components/pubsub.yaml metadata.name)
PUBSUB_NAME = "pubsub"

# Topic names
TODO_EVENTS = "todo.events"
REMINDER_EVENTS = "reminder.events"
RECURRING_EVENTS = "recurring.events"
AI_EVENTS = "ai.events"
AUDIT_EVENTS = "audit.events"

# Dead-letter topic suffix
DLQ_SUFFIX = ".deadletter"
