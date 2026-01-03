"""Chat endpoint for conversational task management."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select
from typing import Optional, List
from datetime import datetime

from ..database import get_session
from ..models import Conversation, Message
from ..auth import get_current_user
from ..agents.todo_agent import run_agent


router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    """Chat request schema."""
    conversation_id: Optional[int] = Field(
        None,
        description="Existing conversation ID (optional, creates new if not provided)"
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User message"
    )


class ToolCall(BaseModel):
    """Tool call information."""
    tool: str
    parameters: dict
    result: dict


class ChatResponse(BaseModel):
    """Chat response schema."""
    conversation_id: int
    response: str
    tool_calls: List[ToolCall]


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """
    Chat endpoint for conversational task management.
    
    This endpoint processes user messages through an AI agent that can
    perform task operations using natural language.
    
    Flow:
    1. Validate user authentication
    2. Create or retrieve conversation
    3. Store user message
    4. Load conversation history (last 10 messages)
    5. Run AI agent with MCP tools
    6. Store assistant response
    7. Return response with tool call details
    
    Args:
        user_id: User identifier from path
        request: Chat request with message and optional conversation_id
        session: Database session
        current_user: Authenticated user from JWT
    
    Returns:
        ChatResponse with conversation_id, response, and tool_calls
    
    Raises:
        403: User doesn't own the conversation
        404: Conversation not found
        500: Agent error
    """
    
    # 1. Validate user authentication
    if current_user != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access another user's conversation"
        )
    
    # 2. Create or retrieve conversation
    if request.conversation_id:
        # Retrieve existing conversation
        conversation = session.get(Conversation, request.conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        # Update timestamp
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
        session.commit()
    else:
        # Create new conversation
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
    
    # 3. Store user message
    user_message = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="user",
        content=request.message
    )
    session.add(user_message)
    session.commit()
    
    # 4. Load conversation history (last 10 messages for context)
    history_query = (
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc())
    )
    all_history = session.exec(history_query).all()
    
    # Get last 10 messages for API context window
    history = all_history[-10:] if len(all_history) > 10 else all_history
    
    # Build message array for agent
    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in history
    ]
    
    # 5. Run AI agent
    try:
        agent_result = await run_agent(user_id, messages)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent error: {str(e)}"
        )
    
    # 6. Store assistant response
    assistant_message = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="assistant",
        content=agent_result["response"]
    )
    session.add(assistant_message)
    session.commit()
    
    # 7. Return response
    return ChatResponse(
        conversation_id=conversation.id,
        response=agent_result["response"],
        tool_calls=[
            ToolCall(**call)
            for call in agent_result.get("tool_calls", [])
        ]
    )


@router.get("/{user_id}/conversations", response_model=List[dict])
async def list_conversations(
    user_id: str,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """
    List all conversations for a user.
    
    Args:
        user_id: User identifier
        session: Database session
        current_user: Authenticated user
    
    Returns:
        List of conversations with metadata
    """
    if current_user != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access another user's conversations"
        )
    
    query = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = session.exec(query).all()
    
    return [
        {
            "id": conv.id,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat()
        }
        for conv in conversations
    ]


@router.get("/{user_id}/conversations/{conversation_id}/messages", response_model=List[dict])
async def get_conversation_messages(
    user_id: str,
    conversation_id: int,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """
    Get all messages for a conversation.
    
    Args:
        user_id: User identifier
        conversation_id: Conversation identifier
        session: Database session
        current_user: Authenticated user
    
    Returns:
        List of messages
    """
    if current_user != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access another user's conversation"
        )
    
    # Verify conversation ownership
    conversation = session.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    messages = session.exec(query).all()
    
    return [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat()
        }
        for msg in messages
    ]
