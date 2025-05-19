from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db import get_db
from models.chat import ChatCreate, UpdateChatPayload, ChatModel
from services.chat import ChatService


router = APIRouter(prefix="/chats", tags=["Chats"])

@router.post("/", response_model=ChatModel)
def create_chat(payload: ChatCreate, db: Session = Depends(get_db)):
    service = ChatService(db)
    return service.create_session(payload)


@router.get("/{chat_id}", response_model=ChatModel)
def get_chat(chat_id: int, db: Session = Depends(get_db)):
    service = ChatService(db)
    chat = service.get_session(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.put("/{chat_id}", response_model=ChatModel)
def update_chat(chat_id: int, payload: UpdateChatPayload, db: Session = Depends(get_db)):
    service = ChatService(db)
    chat = service.update_session(chat_id, payload)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.delete("/{chat_id}")
def delete_chat(chat_id: int, db: Session = Depends(get_db)):
    service = ChatService(db)
    chat = service.get_session(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    db.delete(chat)
    db.commit()
    return {"message": "Chat deleted successfully"}

@router.get("/user/{user_id}", response_model=list[ChatModel])
def get_chat_by_user_id(user_id: int, db: Session = Depends(get_db)):
    service = ChatService(db)
    chats = service.get_chat_by_user_id(user_id)
    return chats
