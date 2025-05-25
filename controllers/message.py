from fastapi import APIRouter, HTTPException, status
from models.chats import ChatMessageCreate, ChatMessageResponse, UpdateMessagePayload
from services.message import MessageService
from typing import Optional, Dict, Any

router = APIRouter(prefix="/messages", tags=["Messages"])

class AgentMessageCreate(ChatMessageCreate):
    agent_id: str
    agent_type: str
    metadata: Optional[Dict[str, Any]] = None

class AgentMessageResponse(ChatMessageResponse):
    agent_id: str
    agent_type: str
    metadata: Optional[Dict[str, Any]] = None

@router.post("/", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(payload: ChatMessageCreate):
    return MessageService.create_message(payload)

@router.get("/{message_id}", response_model=ChatMessageResponse)
def get_message(message_id: int):
    try:
        message = MessageService.get_message(message_id)
        return message
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

@router.put("/{message_id}", response_model=ChatMessageResponse)
def update_message(message_id: int, payload: UpdateMessagePayload):
    try:
        message = MessageService.update_message(message_id, payload)
        return message
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(message_id: int):
    try:
        MessageService.delete_message(message_id)
        return {"message": "Message deleted successfully"}
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

@router.get("/recent/{chat_id}", response_model=list[ChatMessageResponse])
def get_recent_messages(chat_id: int, limit: int = 5):
    messages = MessageService.get_recent_messages(chat_id, limit)
    return messages

@router.get("/all/{chat_id}", response_model=list[ChatMessageResponse])
def get_all_messages_in_chat(chat_id: int, limit:int =  30 ):
    messages = MessageService.get_all_messages_in_chat(chat_id, limit)
    return messages

@router.post("/agent", response_model=AgentMessageResponse, status_code=status.HTTP_201_CREATED)
def create_agent_message(payload: AgentMessageCreate):
    return MessageService.create_agent_message(payload)

@router.get("/agent/{agent_id}", response_model=list[AgentMessageResponse])
def get_agent_messages(agent_id: str, limit: int = 10):
    messages = MessageService.get_agent_messages(agent_id, limit)
    return messages

@router.get("/agent/{agent_id}/chat/{chat_id}", response_model=list[AgentMessageResponse])
def get_agent_chat_messages(agent_id: str, chat_id: int):
    messages = MessageService.get_agent_chat_messages(agent_id, chat_id)
    return messages

@router.post("/sender_and_content/chat/{chat_id}")
def get_sender_type_and_content(chat_id: int, limit: int =  30):
    return MessageService.get_sender_type_and_content(chat_id, limit)