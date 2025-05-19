from db import Session
from models.chat import Chat, ChatCreate, UpdateChatPayload, ChatModel
from models.message import Message


class ChatRepository:
    @staticmethod
    def create(payload: ChatCreate) -> ChatModel:
        with Session() as session:
            # Đếm số lượng session đã có của user_id này
            existing_count = session.query(Chat).filter(Chat.user_id == payload.user_id).count()
            next_session_id = existing_count + 1

            # Tạo bản ghi mới với session_id
            chat = Chat(**payload.model_dump(), session_id=next_session_id)
            session.add(chat)
            session.commit()
            session.refresh(chat)
            return ChatModel.model_validate(chat)

    @staticmethod
    def get_one(chat_id: int) -> ChatModel:
        with Session() as session:
            chat = session.get(Chat, chat_id)
            return ChatModel.model_validate(chat)

    @staticmethod
    def update(chat_id: int, data: UpdateChatPayload) -> ChatModel:
        with Session() as session:
            chat = session.get(Chat, chat_id)
            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(chat, field, value)
            session.commit()
            session.refresh(chat)
            return ChatModel.model_validate(chat)

    @staticmethod
    def delete(chat_id: int):
        with Session() as session:
            # Xóa tất cả message liên quan trước
            session.query(Message).filter(Message.chat_id == chat_id).delete()

            # Sau đó xóa chat
            chat = session.get(Chat, chat_id)
            if chat:
                session.delete(chat)

            session.commit()

    @staticmethod
    def get_chat_by_user_id(user_id: int) -> list[ChatModel]:
        with Session() as session:
            chats = session.query(Chat).filter(Chat.user_id == user_id).all()
            return [ChatModel.model_validate(chat) for chat in chats]
