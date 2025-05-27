from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from repositories.shop_chat import ShopChatRepository
from models.shop_chat import (
    ShopChatSessionCreate,
    ShopChatMessageCreate,
    ShopChatSessionModel,
    ShopChatMessageModel,
    ShopChatHistoryResponse
)
from shop_chat.chat import process_shop_chat
from shop_chat.base import ShopAgentRequest, ShopAgentResponse

class ShopChatService:
    def __init__(self, db: Session):
        self.repository = ShopChatRepository(db)

    async def create_session(self, shop_id: int, agent: str, context: Optional[Dict[str, Any]] = None) -> ShopChatSessionModel:
        """Create a new chat session"""
        session_data = ShopChatSessionCreate(
            shop_id=shop_id,
            agent=agent,
            context=context
        )
        session = self.repository.create_session(session_data)
        return ShopChatSessionModel.from_orm(session)

    async def process_message(self, session_id: int, message: str, role: str = "user") -> ShopAgentResponse:
        """Process a new message in a chat session"""
        # Get the session
        session = self.repository.get_session(session_id)
        if not session:
            raise ValueError("Chat session not found")

        # Create agent request
        agent_request = ShopAgentRequest(
            shop_id=session.shop_id,
            message=message,
            context=session.context
        )

        # Process the message
        response = await process_shop_chat(agent_request)

        # Save the user message
        user_message = ShopChatMessageCreate(
            session_id=session_id,
            role=role,
            content=message
        )
        self.repository.add_message(user_message)

        # Save the agent response
        agent_message = ShopChatMessageCreate(
            session_id=session_id,
            role="assistant",
            content=response.response,
            metadata=response.context
        )
        self.repository.add_message(agent_message)

        # Update session context
        if response.context:
            self.repository.update_session_context(session_id, response.context)

        return response

    async def get_chat_history(self, session_id: int) -> ShopChatHistoryResponse:
        """Get chat history for a session"""
        session = self.repository.get_session(session_id)
        if not session:
            raise ValueError("Chat session not found")

        messages = self.repository.get_session_messages(session_id)

        return ShopChatHistoryResponse(
            session=ShopChatSessionModel.from_orm(session),
            messages=[ShopChatMessageModel.from_orm(msg) for msg in messages]
        )

    async def get_shop_history(self, shop_id: int, limit: int = 10) -> List[ShopChatSessionModel]:
        """Get recent chat history for a shop"""
        sessions = self.repository.get_shop_chat_history(shop_id, limit)
        return [ShopChatSessionModel.from_orm(session) for session in sessions]

    async def delete_session(self, session_id: int) -> bool:
        """Delete a chat session"""
        return self.repository.delete_session(session_id) 


    async def check_shop_by_shop_id(shop_id: int) -> Optional[Shop]:
        """Kiểm tra shop theo shop_id bằng cách gọi lại hàm cùng tên trong repo."""
        return repository.check_shop_by_shop_id(shop_id)
