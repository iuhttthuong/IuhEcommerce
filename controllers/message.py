from fastapi import APIRouter, HTTPException, status
from models.message import CreateMessagePayload, UpdateMessagePayload, MessageModel
from services.message import MessageService

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post("/", response_model=MessageModel, status_code=status.HTTP_201_CREATED)
def create_message(payload: CreateMessagePayload):
    return MessageService.create_message(payload)


@router.get("/{message_id}", response_model=MessageModel)
def get_message(message_id: int):
    try:
        message = MessageService.get_message(message_id)
        return message
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


@router.put("/{message_id}", response_model=MessageModel)
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

@router.get("/recent/{chat_id}", response_model=list[MessageModel])
def get_recent_messages(chat_id: int, limit: int = 5):
    messages = MessageService.get_recent_messages(chat_id, limit)
    return messages


@router.get("/all/{chat_id}", response_model=list[MessageModel])   
def get_all_messages_in_chat(chat_id: int):
    messages = MessageService.get_all_messages_in_chat(chat_id)
    return messages