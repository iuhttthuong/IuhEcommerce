from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db import get_db
from models.chats import ChatCreate, ChatMessageCreate, ChatResponse, ChatMessageResponse
from services.chat import ChatService
from controllers.manager import ask_chatbot, ChatbotRequest
from shop_chat.chat import process_shop_chat, ShopChatRequest, ShopChatResponse
from typing import Dict, Any

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
            shop_request = ShopChatRequest(
                shop_id=payload.sender_id,
                message=payload.content,
                user_id=None,
                context={}
            )
            
            # Process using shop chat
            response = await process_shop_chat(shop_request)
            
            # Save the response to chat history
            service.add_message(ChatMessageCreate(
                chat_id=chat.chat_id,
                sender_type="shop",
                sender_id=payload.sender_id,
                content=response.response
            ))
            
            return {
                "response": response.response,
                "agent": response.agent,
                "timestamp": response.timestamp,
                "context": response.context
            }
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
        print(f"Error processing chat message: {str(e)}")
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

@router.get("/customer/{customer_id}", response_model=list[ChatResponse])
def get_chat_by_customer_id(customer_id: int, db: Session = Depends(get_db)):
    service = ChatService(db)
    chats = service.get_chat_by_customer_id(customer_id)
    return chats

@router.get("/shop/{shop_id}", response_model=list[ChatResponse])
def get_chat_by_shop_id(shop_id: int, db: Session = Depends(get_db)):
    service = ChatService(db)
    chats = service.get_chat_by_shop_id(shop_id)
    return chats
