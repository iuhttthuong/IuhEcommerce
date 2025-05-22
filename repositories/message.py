from sqlalchemy.orm import Session
from models.chats import ChatMessageCreate, ChatMessage, UpdateMessagePayload, ChatMessageResponse
from models.message import MessageModel
from db import Session


class MessageRepository:
    @staticmethod
    def create_message(payload: ChatMessageCreate) -> ChatMessage:
        with Session() as session:
            try:
                message = ChatMessage(**payload.model_dump())
                session.add(message)
                session.commit()
                session.refresh(message)
                return message
            except Exception as e:
                session.rollback()
                raise e

    @staticmethod
    def get_message(message_id: int) -> ChatMessage:
        with Session() as session:
            return session.query(ChatMessage).filter(ChatMessage.id == message_id).first()

    @staticmethod
    def update_message(message_id: int, payload: UpdateMessagePayload) -> ChatMessage:
        with Session() as session:
            message = session.query(ChatMessage).filter(ChatMessage.id == message_id).first()
            if message:
                for key, value in payload.dict(exclude_unset=True).items():
                    setattr(message, key, value)
                session.commit()
                session.refresh(message)
            return message

    @staticmethod
    def delete_message(message_id: int) -> None:
        with Session() as session:
            message = session.query(ChatMessage).filter(ChatMessage.id == message_id).first()
            if message:
                session.delete(message)
                session.commit()

    @staticmethod
    def get_recent_messages(chat_id: int, limit: int = 5) -> list[ChatMessage]:
        with Session() as session:
            return session.query(ChatMessage)\
                .filter(ChatMessage.chat_id == chat_id)\
                .order_by(ChatMessage.created_at.desc())\
                .limit(limit)\
                .all()

    @staticmethod
    def get_all_messages_in_chat(chat_id: int) -> list[ChatMessageResponse]:
        with Session() as session:
            result = session.query(ChatMessage)\
                .filter(ChatMessage.chat_id == chat_id)\
                .order_by(ChatMessage.created_at.asc())\
                .all()
            return [ChatMessageResponse.model_validate(msg) for msg in result]
