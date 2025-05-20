from sqlalchemy.orm import Session
from models.chats import ChatMessageCreate, ChatMessage, UpdateMessagePayload
from db import SessionLocal


class MessageRepository:
    @staticmethod
    def create_message(payload: ChatMessageCreate) -> ChatMessage:
        db = SessionLocal()
        try:
            message = ChatMessage(**payload.dict())
            db.add(message)
            db.commit()
            db.refresh(message)
            return message
        finally:
            db.close()

    @staticmethod
    def get_message(message_id: int) -> ChatMessage:
        db = SessionLocal()
        try:
            return db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        finally:
            db.close()

    @staticmethod
    def update_message(message_id: int, payload: UpdateMessagePayload) -> ChatMessage:
        db = SessionLocal()
        try:
            message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
            if message:
                for key, value in payload.dict(exclude_unset=True).items():
                    setattr(message, key, value)
                db.commit()
                db.refresh(message)
            return message
        finally:
            db.close()

    @staticmethod
    def delete_message(message_id: int) -> None:
        db = SessionLocal()
        try:
            message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
            if message:
                db.delete(message)
                db.commit()
        finally:
            db.close()

    @staticmethod
    def get_recent_messages(chat_id: int, limit: int = 5) -> list[ChatMessage]:
        db = SessionLocal()
        try:
            return db.query(ChatMessage)\
                .filter(ChatMessage.chat_id == chat_id)\
                .order_by(ChatMessage.created_at.desc())\
                .limit(limit)\
                .all()
        finally:
            db.close()

    @staticmethod
    def get_all_messages_in_chat(chat_id: int) -> list[ChatMessage]:
        db = SessionLocal()
        try:
            return db.query(ChatMessage)\
                .filter(ChatMessage.chat_id == chat_id)\
                .order_by(ChatMessage.created_at.asc())\
                .all()
        finally:
            db.close()
