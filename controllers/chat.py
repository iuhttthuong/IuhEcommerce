from fastapi import APIRouter, HTTPException
from models.chat import ChatCreate, UpdateChatPayload, ChatModel
from services.chat import ChatService


router = APIRouter(prefix="/chats", tags=["Chats"])

@router.post("/add", response_model=ChatModel)
def create_chat(payload: ChatCreate):
    return ChatService.create_chat(payload)


@router.get("/get/{chat_id}", response_model=ChatModel)
def get_chat(chat_id):
    chat = ChatService.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.put("update/{chat_id}", response_model=ChatModel)
def update_chat(chat_id, payload: UpdateChatPayload):
    chat = ChatService.update_chat(chat_id, payload)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.delete("/delete/{chat_id}")
def delete_chat(chat_id):
    ChatService.delete_chat(chat_id)
    return {"message": "Chat deleted successfully"}

@router.get("/user/{user_id}", response_model=list[ChatModel])
def get_chat_by_user_id(user_id: int):
    chats = ChatService.get_chat_by_user_id(user_id)
    return chats