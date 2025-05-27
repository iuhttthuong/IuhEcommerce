from typing import List, Optional, Dict, Any
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
import asyncio
from models.shops import Shop
from shop_chat.base import ShopRequest, ChatMessageRequest, process_shop_chat
from shop_chat.shop_manager import ShopManager
from repositories.message import MessageRepository
from datetime import datetime
import logging
import traceback


logger = logging.getLogger(__name__)

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

@router.post("/sessions/{session_id}/messages")
async def process_message(session_id: int, message: str, shop_id: int, db: Session = Depends(get_db)):
    shop_manager = ShopManager(db=db, shop_id=shop_id)
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
        # messages = service.get_messages(session_id)

        # Process with shop chat
        shop_request = ShopRequest(
            message=message,
            chat_id=session_id,
            shop_id=shop_id,
            user_id=None,
            context={},
            entities={},
            agent_messages=[],
            filters={}
        )

        # Process using shop chat
        response = await process_shop_chat(shop_request)
        logger.info(f"Response from shop chat: {response}")
        logger.info(f"Response type: {type(response)}")
        print(f"✅🤦‍♀️➡️❎💣😊🙌😁Response: {response}")
        answer = shop_manager.process_chat_message(message, response, shop_id, session_id)
        if asyncio.iscoroutine(answer):
            answer = await answer
        logger.info(f"Answer from shop manager: {answer}")

        # Ensure the message content is a string
        message_content = answer.get("message")
        if message_content is None:
            message_content = "Không có phản hồi từ hệ thống."
        elif not isinstance(message_content, str):
            message_content = str(message_content)

        service.add_message(
            ChatMessageCreate(
                chat_id=session_id,
                sender_type="agent_response",
                sender_id=shop_id,
                content=message_content,
                message_metadata=response.get("context", {} if isinstance(response, dict) else {})
            )
        )

        return message_content
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in process_message: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

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

@router.post("/chats/message")
async def create_chat_message(request: ChatMessageRequest, db: Session = Depends(get_db)):
    try:
        # Convert to ShopRequest format
        shop_request = ShopRequest(
            message=request.content,
            chat_id=request.chat_id,
            shop_id=request.sender_id if request.sender_type == "shop" else None,
            user_id=request.sender_id if request.sender_type == "user" else None,
            context=request.message_metadata if request.message_metadata else {},
            entities={},
            agent_messages=[],
            filters={}
        )

        # Process the request
        response = await process_shop_chat(shop_request)

        # Save the message to database
        message_repository = MessageRepository()
        message = ChatMessageCreate(
            chat_id=request.chat_id,
            sender_type=request.sender_type,
            sender_id=request.sender_id,
            content=request.content,
            message_metadata=request.message_metadata
        )
        message_repository.create_message(message)

        return response
    except Exception as e:
        logger.error(f"Error in create_chat_message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 


@router.post("/check/{shop_id}")
async def check_shop(shop_id: int, db: Session = Depends(get_db)):
    """
    Check shop status or information.
    """
    # Giả sử bạn có MessageRepository hoặc ShopRepository, ví dụ:
    # shop = ShopRepository(db).get_shop_by_id(shop_id)
    # Nếu không có, bạn có thể truy vấn trực tiếp bằng SQLAlchemy

    # Ví dụ truy vấn trực tiếp:
    shop = db.query(Shop).filter(Shop.shop_id == shop_id).first()

    return  shop is not None
