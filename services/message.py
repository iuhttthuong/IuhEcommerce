import uuid
from models.message import CreateMessagePayload, UpdateMessagePayload, MessageModel
from repositories.message import MessageRepository


class MessageService:
    @staticmethod
    def create_message(payload: CreateMessagePayload) -> MessageModel:
        return MessageRepository.create(payload)

    @staticmethod
    def get_message(message_id: int) -> MessageModel:
        return MessageRepository.get_one(message_id)

    @staticmethod
    def update_message(message_id: int, data: UpdateMessagePayload) -> MessageModel:
        return MessageRepository.update(message_id, data)

    @staticmethod
    def delete_message(message_id: int) -> None:
        return MessageRepository.delete(message_id)

    @staticmethod
    def get_recent_messages(chat_id: int, limit: int = 5) -> list[MessageModel]:
        return MessageRepository.get_recent_messages(chat_id, limit)

    @staticmethod
    def get_all_messages_in_chat(chat_id: int) -> list[MessageModel]:
        return MessageRepository.get_all_messages_in_chat(chat_id)
