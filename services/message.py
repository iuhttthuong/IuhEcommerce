import uuid
from models.chats import ChatMessageCreate, ChatMessageResponse, UpdateMessagePayload
from repositories.message import MessageRepository


class MessageService:
    @staticmethod
    def create_message(payload: ChatMessageCreate) -> ChatMessageResponse:
        message = MessageRepository.create_message(payload)
        return ChatMessageResponse.model_validate(message)

    @staticmethod
    def get_message(message_id: int) -> ChatMessageResponse:
        message = MessageRepository.get_message(message_id)
        if not message:
            raise ValueError(f"Message with ID {message_id} not found")
        return ChatMessageResponse.model_validate(message)

    @staticmethod
    def update_message(message_id: int, payload: UpdateMessagePayload) -> ChatMessageResponse:
        message = MessageRepository.update_message(message_id, payload)
        if not message:
            raise ValueError(f"Message with ID {message_id} not found")
        return ChatMessageResponse.model_validate(message)

    @staticmethod
    def delete_message(message_id: int) -> None:
        MessageRepository.delete_message(message_id)

    @staticmethod
    def get_recent_messages(chat_id: int, limit: int = 5) -> list[ChatMessageResponse]:
        messages = MessageRepository.get_recent_messages(chat_id, limit)
        return [ChatMessageResponse.model_validate(msg) for msg in messages]

    @staticmethod
    def get_all_messages_in_chat(chat_id: int) -> list[ChatMessageResponse]:
        messages = MessageRepository.get_all_messages_in_chat(chat_id)
        return [ChatMessageResponse.model_validate(msg) for msg in messages]
