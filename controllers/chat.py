from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db import get_db
from models.chats import ChatCreate, ChatMessageCreate, ChatResponse, ChatMessageResponse
from services.chat import ChatService
from controllers.manager import ask_chatbot, ChatbotRequest
from shop_chat.chat import process_shop_chat
from repositories.message import MessageRepository
from shop_chat.base import ShopRequest, ChatMessageRequest
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from repositories.chat import ChatRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chats", tags=["Chats"])

@router.post("/", response_model=ChatResponse)
def create_chat(payload: ChatCreate, db: Session = Depends(get_db)):
    # Loại bỏ shop_id, chỉ tạo chat với customer_id
    service = ChatService(db)
    # Tạo chat chỉ với customer_id, không truyền shop_id
    return service.create_session(ChatCreate(customer_id=payload.customer_id))

@router.post("/message")
async def process_message(payload: ChatMessageCreate, db: Session = Depends(get_db)):
    """
    Process chat messages and route to appropriate handler based on chat type
    """
    service = ChatService(db)
    
    try:
        # Create or get chat session
        chat = service.create_session(ChatCreate(
            shop_id=int(payload.sender_id) if payload.sender_type == "shop" else 1,  # Use sender_id as shop_id for shop messages
            customer_id=payload.sender_id if payload.sender_type == "customer" else None
        ))
        
        if payload.sender_type == "shop":
            # Process shop chat
            shop_request = ShopRequest(
                message=payload.content,
                chat_id=chat.chat_id,
                shop_id=payload.sender_id,
                user_id=None,
                context={},
                entities={},
                agent_messages=[],
                filters={}
            )
            
            # Process using shop chat
            response = await process_shop_chat(shop_request)
            
            # Save the response to chat history
            service.add_message(ChatMessageCreate(
                chat_id=chat.chat_id,
                sender_type="shop",
                sender_id=payload.sender_id,
                content=response["response"]["content"]
            ))
            
            return response
        else:
            # Process customer chat
            chatbot_request = ChatbotRequest(
                chat_id=chat.chat_id,
                message=payload.content,
                context={},
                user_id=payload.sender_id
            )
            
            # Get response from manager
            manager_response = await ask_chatbot(chatbot_request)
            
            # Save the response to chat history
            service.add_message(ChatMessageCreate(
                chat_id=chat.chat_id,
                sender_type="customer",
                sender_id=payload.sender_id,
                content=manager_response.get("message", "Xin lỗi, tôi không thể xử lý yêu cầu của bạn.")
            ))
            
            return manager_response
            
    except Exception as e:
        # Log the error
        logger.error(f"Error processing chat message: {str(e)}")
        # Return a friendly error message
        return {
            "message": "Xin lỗi, đã có lỗi xảy ra khi xử lý tin nhắn của bạn. Vui lòng thử lại sau.",
            "type": "error",
            "error": str(e)
        }

@router.get("/{chat_id}", response_model=ChatResponse)
def get_chat(chat_id: int, db: Session = Depends(get_db)):
    service = ChatService(db)
    chat = service.get_session(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@router.get("/{chat_id}/messages", response_model=list[ChatMessageResponse])
def get_chat_messages(chat_id: int, db: Session = Depends(get_db)):
    service = ChatService(db)
    messages = service.get_messages(chat_id)
    return messages

@router.delete("/{chat_id}")
def delete_chat(chat_id: int, db: Session = Depends(get_db)):
    service = ChatService(db)
    chat = service.get_session(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    db.delete(chat)
    db.commit()
    return {"message": "Chat deleted successfully"}


@router.get("/customer11/{customer_id}", response_model= List[str] )
def get_chat_by_customer_id11(customer_id: int, db):
    service = ChatService(db)
    chats = service.get_chat_titles_by_customer_id(customer_id)
    return chats


@router.get("/customer/{customer_id}", response_model=list[ChatResponse])
def get_chat_by_customer_id(customer_id: int, db: Session = Depends(get_db)):

    a = get_chat_by_customer_id11(customer_id, db)
    service = ChatService(db)
    chats = service.get_chat_by_customer_id(customer_id)
    return chats


@router.get("/shop11/{shop_id}", response_model = List[str])
def get_chat_by_shop_id11(shop_id: int, db):
    service = ChatService(db)
    chats = service.get_chat_titles_by_shop_id(shop_id)
    return chats


@router.get("/shop/{shop_id}", response_model=list[ChatResponse])
def get_chat_by_shop_id(shop_id: int, db: Session = Depends(get_db)):

    service = ChatService(db)
    a = get_chat_by_shop_id11(shop_id, db)
    chats = service.get_chat_by_shop_id(shop_id)
    return chats

@router.post("/customer/chat/chats/message")
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


@router.get("/titles/", response_model = str)
def get_title_by_chat_id(chat_id: int, db: Session = Depends(get_db)) -> str:
    """
    Get chat titles by chat ID
    """
    service = ChatService(db)
    chats = service.get_title_by_chat_id(chat_id)
    return chats
