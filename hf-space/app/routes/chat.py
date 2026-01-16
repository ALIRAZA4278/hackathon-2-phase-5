"""
Chat API routes for AI Chatbot.
Per specs/001-ai-chatbot/contracts/chat-api.yaml
"""
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
    """
    # Verify user access (URL user_id must match JWT user_id)
    verify_user_access(user_id, current_user)

    # Get or create conversation
    conversation = get_or_create_conversation(
        db, user_id, request.conversation_id
    )

    # Load conversation history
    history = load_conversation_history(db, conversation.id, user_id)

    # Save user message
    save_message(db, conversation.id, user_id, "user", request.message)

    # Run the AI agent
    try:
        response_content = await run_agent(
            user_id=user_id,
            user_message=request.message,
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
