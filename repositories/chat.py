from db import Session
from models.chats import Chat, ChatCreate, ChatResponse, ChatMessage


class ChatRepository:
    @staticmethod
    def create(payload: ChatCreate) -> ChatResponse:
        with Session() as session:
            chat = Chat(**payload.model_dump())
            session.add(chat)
            session.commit()
            session.refresh(chat)
            return ChatResponse.model_validate(chat)

    @staticmethod
    def get_one(chat_id: int) -> ChatResponse:
        with Session() as session:
            chat = session.get(Chat, chat_id)
            return ChatResponse.model_validate(chat)

    @staticmethod
    def update(chat_id: int, data: dict) -> ChatResponse:
        with Session() as session:
            chat = session.get(Chat, chat_id)
            for field, value in data.items():
                setattr(chat, field, value)
            session.commit()
            session.refresh(chat)
            return ChatResponse.model_validate(chat)

    @staticmethod
    def delete(chat_id: int):
        with Session() as session:
            # Xóa tất cả message liên quan trước
            session.query(ChatMessage).filter(ChatMessage.chat_id == chat_id).delete()

            # Sau đó xóa chat
            chat = session.get(Chat, chat_id)
            if chat:
                session.delete(chat)

            session.commit()

    @staticmethod
    def get_chat_by_user_id(user_id: int) -> list[ChatResponse]:
        with Session() as session:
            chats = session.query(Chat).filter(Chat.customer_id == user_id).all()
            return [ChatResponse.model_validate(chat) for chat in chats]
