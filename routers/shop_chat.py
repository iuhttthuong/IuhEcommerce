from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from services.chat import ChatService
from models.chats import (
    ChatCreate,
    ChatMessageCreate,
    ChatResponse,
    ChatMessageResponse
)
from shop_chat.base import ShopChatResponse, ShopChatRequest, process_shop_chat

router = APIRouter(
    prefix="/api/shop-chat",
    tags=["shop-chat"]
)

@router.post("/sessions", response_model=ChatResponse)
async def create_session(
    shop_id: int,
    db: Session = Depends(get_db)
):
    """Create a new chat session"""
    service = ChatService(db)
    return service.create_session(ChatCreate(shop_id=shop_id))

@router.post("/sessions/{session_id}/messages", response_model=ShopChatResponse)
async def process_message(
    session_id: int,
    message: str,
    shop_id: int,
    db: Session = Depends(get_db)
):
    """Process a new message in a chat session"""
    service = ChatService(db)
    try:
        # Add message to chat
        service.add_message(ChatMessageCreate(
            chat_id=session_id,
            sender_type="shop",
            sender_id=shop_id,
            content=message
        ))
        
        # Get chat history
        messages = service.get_messages(session_id)
        
        # Process with shop chat
        shop_request = ShopChatRequest(
            shop_id=shop_id,
            message=message,
            user_id=None,
            context={}
        )
        
        # Process using shop chat
        response = await process_shop_chat(shop_request)
        
        # Save the response to chat history
        service.add_message(ChatMessageCreate(
            chat_id=session_id,
            sender_type="shop",
            sender_id=shop_id,
            content=response.response
        ))
        
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/sessions/{session_id}/history", response_model=List[ChatMessageResponse])
async def get_chat_history(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Get chat history for a session"""
    service = ChatService(db)
    try:
        return service.get_messages(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/shops/{shop_id}/history", response_model=List[ChatResponse])
async def get_shop_history(
    shop_id: int,
    limit: Optional[int] = 10,
    db: Session = Depends(get_db)
):
    """Get recent chat history for a shop"""
    service = ChatService(db)
    return service.get_chat_by_shop_id(shop_id)[:limit]

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Delete a chat session"""
    service = ChatService(db)
    try:
        service.close_session(session_id)
        return {"message": "Chat session closed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) 