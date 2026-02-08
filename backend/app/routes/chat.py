"""
Chat API routes for AI Chatbot.
Per specs/001-ai-chatbot/contracts/chat-api.yaml
Phase V extensions: input sanitization (T051), rate limiting (T052)
"""
import re
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db import get_db
from app.models import Conversation, Message
from app.schemas import (
    ChatRequest,
    ChatResponse,
    MessageResponse,
    ConversationListResponse,
    ConversationResponse,
    MessageListResponse,
)
from app.dependencies import get_current_user, verify_user_access
from app.agent import run_agent


router = APIRouter(tags=["Chat"])


# ============================================================================
# T052: In-memory Rate Limiter (200 req/min per user)
# ============================================================================

# Dict of user_id -> list of request timestamps
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_MAX_REQUESTS = 200
RATE_LIMIT_WINDOW_SECONDS = 60


def check_rate_limit(user_id: str) -> None:
    """
    Check if a user has exceeded the rate limit (200 req/min).
    Cleans up old timestamps outside the window.

    Args:
        user_id: The authenticated user's ID

    Raises:
        HTTPException 429 if rate limit exceeded
    """
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS

    # Clean up old timestamps
    timestamps = _rate_limit_store[user_id]
    _rate_limit_store[user_id] = [ts for ts in timestamps if ts > window_start]

    # Check limit
    if len(_rate_limit_store[user_id]) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 200 requests per minute. Please try again shortly."
        )

    # Record this request
    _rate_limit_store[user_id].append(now)


# ============================================================================
# T051: Input Sanitization (Prompt Injection Defense)
# ============================================================================

# Patterns to strip from user messages (case-insensitive)
_INJECTION_PATTERNS = [
    r"ignore\s+previous\s+instructions?",
    r"ignore\s+all\s+previous\s+instructions?",
    r"ignore\s+above\s+instructions?",
    r"disregard\s+previous\s+instructions?",
    r"disregard\s+all\s+previous\s+instructions?",
    r"forget\s+previous\s+instructions?",
    r"forget\s+all\s+previous\s+instructions?",
    r"override\s+previous\s+instructions?",
    r"^system\s*:",
    r"you\s+are\s+now\b",
    r"act\s+as\s+if\s+you\s+are",
    r"pretend\s+you\s+are",
    r"new\s+instructions?\s*:",
    r"<\s*system\s*>",
    r"<\s*/\s*system\s*>",
    r"\[SYSTEM\]",
    r"\[INST\]",
    r"\[/INST\]",
]

# Compile patterns once for performance
_COMPILED_INJECTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE) for pattern in _INJECTION_PATTERNS
]


def sanitize_message(message: str) -> str:
    """
    Strip common prompt injection patterns from user input.

    Args:
        message: Raw user message

    Returns:
        Sanitized message with injection patterns removed
    """
    sanitized = message
    for pattern in _COMPILED_INJECTION_PATTERNS:
        sanitized = pattern.sub("", sanitized)

    # Clean up extra whitespace from removals
    sanitized = re.sub(r"\s{2,}", " ", sanitized).strip()

    # If the message was entirely injection content, return a safe fallback
    if not sanitized:
        return message.strip()

    return sanitized


# ============================================================================
# Helper Functions
# ============================================================================

def get_or_create_conversation(
    db: Session,
    user_id: str,
    conversation_id: Optional[int] = None
) -> Conversation:
    """
    Get existing conversation or create a new one.

    Args:
        db: Database session
        user_id: The authenticated user's ID
        conversation_id: Optional existing conversation ID

    Returns:
        Conversation object

    Raises:
        HTTPException 404: If conversation_id provided but not found
    """
    if conversation_id:
        # Try to get existing conversation
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        conversation = db.exec(statement).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        return conversation

    # Create new conversation
    conversation = Conversation(
        user_id=user_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def load_conversation_history(
    db: Session,
    conversation_id: int,
    user_id: str,
    limit: int = 50
) -> list[dict]:
    """
    Load message history for a conversation.

    Args:
        db: Database session
        conversation_id: The conversation ID
        user_id: The authenticated user's ID (for security)
        limit: Maximum number of messages to load

    Returns:
        List of message dictionaries for OpenAI API format
    """
    statement = (
        select(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.user_id == user_id
        )
        .order_by(Message.created_at.asc())
        .limit(limit)
    )
    messages = db.exec(statement).all()

    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]


def save_message(
    db: Session,
    conversation_id: int,
    user_id: str,
    role: str,
    content: str
) -> Message:
    """
    Save a message to the database.

    Args:
        db: Database session
        conversation_id: The conversation ID
        user_id: The authenticated user's ID
        role: Message role ('user' or 'assistant')
        content: Message content

    Returns:
        Created Message object
    """
    message = Message(
        user_id=user_id,
        conversation_id=conversation_id,
        role=role,
        content=content,
        created_at=datetime.now(timezone.utc)
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def update_conversation_timestamp(db: Session, conversation_id: int) -> None:
    """
    Update the conversation's updated_at timestamp.

    Args:
        db: Database session
        conversation_id: The conversation ID
    """
    statement = select(Conversation).where(Conversation.id == conversation_id)
    conversation = db.exec(statement).first()
    if conversation:
        conversation.updated_at = datetime.now(timezone.utc)
        db.add(conversation)
        db.commit()


# ============================================================================
# Chat Endpoints
# ============================================================================

@router.post("/{user_id}/chat", response_model=ChatResponse)
async def send_chat_message(
    user_id: str,
    request: ChatRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a chat message to the AI assistant.

    The assistant can manage tasks via MCP tools.
    Returns the assistant's response.

    Security:
    - JWT token required
    - URL user_id must match JWT user_id
    - All tool operations use authenticated user_id
    - Input sanitization applied (T051)
    - Rate limiting enforced (T052)
    """
    # Verify user access (URL user_id must match JWT user_id)
    verify_user_access(user_id, current_user)

    # T052: Check rate limit
    check_rate_limit(user_id)

    # T051: Sanitize user message
    sanitized_message = sanitize_message(request.message)

    # Get or create conversation
    conversation = get_or_create_conversation(
        db, user_id, request.conversation_id
    )

    # Load conversation history
    history = load_conversation_history(db, conversation.id, user_id)

    # Save user message (store original for audit, use sanitized for AI)
    save_message(db, conversation.id, user_id, "user", request.message)

    # Run the AI agent with sanitized input
    try:
        response_content = await run_agent(
            user_id=user_id,
            user_message=sanitized_message,
            conversation_history=history
        )
    except Exception as e:
        # Handle agent errors gracefully
        response_content = "I'm having trouble processing your request. Please try again."

    # Save assistant response
    assistant_message = save_message(
        db, conversation.id, user_id, "assistant", response_content
    )

    # Update conversation timestamp
    update_conversation_timestamp(db, conversation.id)

    # Return response
    return ChatResponse(
        conversation_id=conversation.id,
        message=MessageResponse(
            id=assistant_message.id,
            role="assistant",
            content=response_content,
            created_at=assistant_message.created_at.isoformat()
        )
    )


@router.get("/{user_id}/conversations", response_model=ConversationListResponse)
async def list_conversations(
    user_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all conversations for the authenticated user.

    Returns conversations ordered by most recently updated.
    """
    # Verify user access
    verify_user_access(user_id, current_user)

    # Query conversations
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = db.exec(statement).all()

    return ConversationListResponse(
        conversations=[
            ConversationResponse(
                id=conv.id,
                created_at=conv.created_at.isoformat(),
                updated_at=conv.updated_at.isoformat()
            )
            for conv in conversations
        ]
    )


@router.get(
    "/{user_id}/conversations/{conversation_id}/messages",
    response_model=MessageListResponse
)
async def get_conversation_messages(
    user_id: str,
    conversation_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all messages for a specific conversation.

    Returns messages ordered by creation time (oldest first).
    """
    # Verify user access
    verify_user_access(user_id, current_user)

    # Verify conversation exists and belongs to user
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )
    conversation = db.exec(statement).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Get messages
    statement = (
        select(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.user_id == user_id
        )
        .order_by(Message.created_at.asc())
    )
    messages = db.exec(statement).all()

    return MessageListResponse(
        messages=[
            MessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at.isoformat()
            )
            for msg in messages
        ]
    )
