from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from models.shop_chat import ShopChatSession, ShopChatMessage, ShopChatSessionCreate, ShopChatMessageCreate
from datetime import datetime

class ShopChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, session_data: ShopChatSessionCreate) -> ShopChatSession:
        """Create a new chat session"""
        session = ShopChatSession(
            shop_id=session_data.shop_id,
            agent=session_data.agent,
            context=session_data.context
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: int) -> Optional[ShopChatSession]:
        """Get a chat session by ID"""
        return self.db.query(ShopChatSession).filter(ShopChatSession.id == session_id).first()

    def get_sessions_by_shop(self, shop_id: int) -> List[ShopChatSession]:
        """Get all chat sessions for a shop"""
        return self.db.query(ShopChatSession).filter(ShopChatSession.shop_id == shop_id).all()

    def add_message(self, message_data: ShopChatMessageCreate) -> ShopChatMessage:
        """Add a new message to a chat session"""
        message = ShopChatMessage(
            session_id=message_data.session_id,
            role=message_data.role,
            content=message_data.content,
            metadata=message_data.metadata
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_session_messages(self, session_id: int) -> List[ShopChatMessage]:
        """Get all messages for a chat session"""
        return self.db.query(ShopChatMessage).filter(ShopChatMessage.session_id == session_id).all()

    def update_session_context(self, session_id: int, context: Dict[str, Any]) -> Optional[ShopChatSession]:
        """Update the context of a chat session"""
        session = self.get_session(session_id)
        if session:
            session.context = context
            session.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(session)
        return session

    def delete_session(self, session_id: int) -> bool:
        """Delete a chat session and all its messages"""
        session = self.get_session(session_id)
        if session:
            self.db.delete(session)
            self.db.commit()
            return True
        return False

    def get_shop_chat_history(self, shop_id: int, limit: int = 10) -> List[ShopChatSession]:
        """Get recent chat history for a shop"""
        return self.db.query(ShopChatSession)\
            .filter(ShopChatSession.shop_id == shop_id)\
            .order_by(ShopChatSession.updated_at.desc())\
            .limit(limit)\
            .all() 