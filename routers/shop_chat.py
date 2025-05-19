from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from database import get_db
from services.chat import ChatService
from models.chat import (
    ChatSessionCreate, ChatSessionUpdate,
    ChatMessageCreate, ChatHistoryResponse,
    ChatSessionResponse, ChatMessageResponse
)
from shop.chat_models import ShopChatSession, ShopChatSessionCreate, ShopChatSessionUpdate, ShopChatSessionResponse

router = APIRouter(prefix="/api/shop/chat", tags=["shop_chat"])

@router.post("/sessions", response_model=ShopChatSessionResponse)
def create_chat_session(
    data: ShopChatSessionCreate,
    db: Session = Depends(get_db)
):
    """Create a new chat session for a shop."""
    chat_service = ChatService(db)
    return chat_service.create_session(data)

@router.get("/sessions/{session_id}", response_model=ShopChatSessionResponse)
def get_chat_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific chat session."""
    chat_service = ChatService(db)
    session = chat_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session

@router.put("/sessions/{session_id}", response_model=ShopChatSessionResponse)
def update_chat_session(
    session_id: int,
    data: ShopChatSessionUpdate,
    db: Session = Depends(get_db)
):
    """Update a chat session."""
    chat_service = ChatService(db)
    return chat_service.update_session(session_id, data)

@router.post("/messages", response_model=ChatMessageResponse)
def add_message(
    data: ChatMessageCreate,
    db: Session = Depends(get_db)
):
    """Add a new message to a chat session."""
    chat_service = ChatService(db)
    return chat_service.add_message(data)

@router.get("/sessions/{session_id}/history", response_model=ChatHistoryResponse)
def get_chat_history(
    session_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get chat history for a session."""
    chat_service = ChatService(db)
    return chat_service.get_chat_history(session_id, limit)

@router.get("/shops/{shop_id}/active-sessions", response_model=List[ShopChatSessionResponse])
def get_active_sessions(
    shop_id: int,
    db: Session = Depends(get_db)
):
    """Get all active chat sessions for a shop."""
    chat_service = ChatService(db)
    return chat_service.get_active_sessions(shop_id)

@router.post("/sessions/{session_id}/close", response_model=ShopChatSessionResponse)
def close_chat_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Close a chat session."""
    chat_service = ChatService(db)
    return chat_service.close_session(session_id)

@router.get("/sessions/{session_id}/summary", response_model=Dict[str, Any])
def get_session_summary(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Get a summary of a chat session."""
    chat_service = ChatService(db)
    return chat_service.get_session_summary(session_id)

@router.get("/shops/{shop_id}/analytics", response_model=Dict[str, Any])
def get_shop_chat_analytics(
    shop_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get chat analytics for a shop."""
    chat_service = ChatService(db)
    return chat_service.get_shop_chat_analytics(shop_id, days) 