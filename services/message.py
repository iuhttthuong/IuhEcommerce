from models.chats import ChatMessageCreate, ChatMessageResponse, UpdateMessagePayload
from repositories.message import MessageRepository
from typing import List


class MessageService:
    @staticmethod
    def create_message(payload: ChatMessageCreate) -> ChatMessageResponse:
        return MessageRepository.create_message(payload)

    @staticmethod
    def get_message(message_id: int) -> ChatMessageResponse:
        return MessageRepository.get_message(message_id)

    @staticmethod
    def update_message(message_id: int, payload: UpdateMessagePayload) -> ChatMessageResponse:
        return MessageRepository.update_message(message_id, payload)

    @staticmethod
    def delete_message(message_id: int) -> None:
        MessageRepository.delete_message(message_id)

    @staticmethod
    def get_recent_messages(chat_id: int, limit: int = 5) -> List[ChatMessageResponse]:
        return MessageRepository.get_recent_messages(chat_id, limit)

    @staticmethod
    def get_all_messages_in_chat(chat_id: int, limit = 30) -> List[ChatMessageResponse]:
        return MessageRepository.get_all_messages_in_chat(chat_id, limit)

    @staticmethod
    def create_agent_message(payload: ChatMessageCreate) -> ChatMessageResponse:
        # Add agent-specific metadata
        if not payload.metadata:
            payload.metadata = {}
        payload.metadata["is_agent_message"] = True
        return MessageRepository.create_message(payload)

    @staticmethod
    def get_agent_messages(agent_id: str, limit: int = 10) -> List[ChatMessageResponse]:
        return MessageRepository.get_messages_by_sender(agent_id, limit)

    @staticmethod
    def get_agent_chat_messages(agent_id: str, chat_id: int) -> List[ChatMessageResponse]:
        return MessageRepository.get_messages_by_sender_and_chat(agent_id, chat_id)

    @staticmethod
    def get_agent_conversation_history(agent_id: str, chat_id: int, limit: int = 10) -> List[ChatMessageResponse]:
        return MessageRepository.get_conversation_history(agent_id, chat_id, limit)

    @staticmethod
    def get_sender_type_and_content(chat_id: int, limit=30) -> list[dict]:
        return MessageRepository.get_sender_type_and_content(chat_id, limit)
    
    