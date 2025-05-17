from models.chat import ChatCreate, UpdateChatPayload, ChatModel
from repositories.chat import ChatRepository


class ChatService:
    @staticmethod
    def create_chat(payload: ChatCreate) -> ChatModel:
        return ChatRepository.create(payload)

    @staticmethod
    def get_chat(chat_id: int) -> ChatModel:
        return ChatRepository.get_one(chat_id)

    @staticmethod
    def update_chat(chat_id: int, data: UpdateChatPayload) -> ChatModel:
        return ChatRepository.update(chat_id, data)

    @staticmethod
    def delete_chat(chat_id: int) -> None:
        return ChatRepository.delete(chat_id)

    @staticmethod
    def get_chat_by_user_id(user_id: int) -> list[ChatModel]:
        return ChatRepository.get_chat_by_user_id(user_id)