from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from fastapi import HTTPException
from models.chat import (
    Chat, ChatMessage,
    ChatCreate, UpdateChatPayload, ChatModel,
    ChatHistoryResponse
)
from models.shop import Shop
from models.customers import Customer
from .shop import ShopService

class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.shop_service = ShopService(db)

    def create_session(self, data: ChatCreate) -> Chat:
        # Determine chat type based on shop_id and user_id
        if data.shop_id == 0 and data.user_id > 0:
            # Customer chat
            data.role = "customer"
        elif data.user_id == 0 and data.shop_id > 0:
            # Shop chat
            data.role = "shop"
        else:
            raise HTTPException(
                status_code=400, 
                detail="Invalid chat configuration. Must have either shop_id=0 and user_id>0 for customer chat, or user_id=0 and shop_id>0 for shop chat"
            )

        # Verify shop exists if shop_id is provided
        if data.shop_id > 0:
            shop = self.shop_service.get_shop(data.shop_id)
            if not shop:
                raise HTTPException(status_code=404, detail="Shop not found")

        session = Chat(
            shop_id=data.shop_id,
            user_id=data.user_id,
            role=data.role,
            context=data.context
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: int) -> Optional[Chat]:
        return self.db.query(Chat).filter(Chat.id == session_id).first()

    def update_session(self, session_id: int, data: UpdateChatPayload) -> Chat:
        session = self.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")

        update_data = data.dict(exclude_unset=True)
        
        # Validate user_id if it's being updated
        if 'user_id' in update_data:
            user_id = update_data['user_id']
            if user_id > 0:  # Only validate if user_id is positive
                customer = self.db.query(Customer).filter(Customer.customer_id == user_id).first()
                if not customer:
                    raise HTTPException(status_code=404, detail="Customer not found")
            elif user_id == 0:  # If user_id is 0, ensure this is a shop chat
                if session.role != "shop":
                    raise HTTPException(
                        status_code=400,
                        detail="Cannot set user_id to 0 for non-shop chats"
                    )

        for field, value in update_data.items():
            setattr(session, field, value)
        session.updated_at = datetime.now()

        self.db.commit()
        self.db.refresh(session)
        return session

    def add_message(self, data: ChatCreate) -> ChatMessage:
        # Try to get existing session
        session = self.get_session(data.chat_id)
        
        # If session doesn't exist, create a new one
        if not session:
            session = self.create_session(data)
            data.chat_id = session.id

        message = ChatMessage(
            chat_id=data.chat_id,
            role=data.role,
            content=data.content,
            message_metadata=data.message_metadata
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_chat_history(self, session_id: int, limit: int = 50) -> ChatHistoryResponse:
        session = self.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")

        messages = self.db.query(ChatMessage).filter(
            ChatMessage.chat_id == session_id
        ).order_by(
            ChatMessage.timestamp.asc()
        ).limit(limit).all()

        return ChatHistoryResponse(session=session, messages=messages)

    def get_active_sessions(self, shop_id: int) -> List[Chat]:
        return self.db.query(Chat).filter(
            Chat.shop_id == shop_id,
            Chat.status == "active"
        ).all()

    def close_session(self, session_id: int) -> Chat:
        return self.update_session(session_id, UpdateChatPayload(status="closed"))

    def get_session_summary(self, session_id: int) -> Dict[str, Any]:
        session = self.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")

        messages = self.get_chat_history(session_id).messages
        return {
            "id": session.id,
            "shop_id": session.shop_id,
            "user_id": session.user_id,
            "message_count": len(messages),
            "last_message": messages[-1].timestamp if messages else session.created_at,
            "status": session.status,
            "created_at": session.created_at,
            "updated_at": session.updated_at
        }

    def get_shop_chat_analytics(self, shop_id: int, days: int = 30) -> Dict[str, Any]:
        start_date = datetime.now() - timedelta(days=days)

        # Get total and active sessions
        total_sessions = self.db.query(func.count(Chat.id)).filter(
            Chat.shop_id == shop_id,
            Chat.created_at >= start_date
        ).scalar()

        active_sessions = self.db.query(func.count(Chat.id)).filter(
            Chat.shop_id == shop_id,
            Chat.status == "active",
            Chat.updated_at >= start_date
        ).scalar()

        # Get average messages per session
        total_messages = self.db.query(func.count(ChatMessage.id)).filter(
            ChatMessage.chat_id.in_(
                self.db.query(Chat.id).filter(
                    Chat.shop_id == shop_id,
                    Chat.created_at >= start_date
                )
            )
        ).scalar()

        avg_messages = total_messages / total_sessions if total_sessions > 0 else 0

        # Get common topics
        common_topics = self.db.query(
            ChatMessage.message_metadata['topics'].astext,
            func.count(ChatMessage.id)
        ).filter(
            ChatMessage.chat_id.in_(
                self.db.query(Chat.id).filter(
                    Chat.shop_id == shop_id,
                    Chat.created_at >= start_date
                )
            ),
            ChatMessage.message_metadata['topics'].isnot(None)
        ).group_by(
            ChatMessage.message_metadata['topics'].astext
        ).order_by(
            desc(func.count(ChatMessage.id))
        ).limit(10).all()

        # Get average response time
        response_times = []
        messages = self.db.query(ChatMessage).filter(
            ChatMessage.chat_id.in_(
                self.db.query(Chat.id).filter(
                    Chat.shop_id == shop_id,
                    Chat.created_at >= start_date
                )
            )
        ).order_by(
            ChatMessage.chat_id,
            ChatMessage.timestamp
        ).all()

        for i in range(1, len(messages)):
            if messages[i].role == "assistant" and messages[i-1].role == "user":
                response_time = (messages[i].timestamp - messages[i-1].timestamp).total_seconds()
                response_times.append(response_time)

        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        # Get peak hours
        peak_hours = {}
        for hour in range(24):
            count = self.db.query(func.count(ChatMessage.id)).filter(
                ChatMessage.chat_id.in_(
                    self.db.query(Chat.id).filter(
                        Chat.shop_id == shop_id,
                        Chat.created_at >= start_date
                    )
                ),
                func.extract('hour', ChatMessage.timestamp) == hour
            ).scalar()
            peak_hours[str(hour)] = count

        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "average_messages_per_session": avg_messages,
            "common_topics": [{"topic": t[0], "count": t[1]} for t in common_topics],
            "average_response_time": avg_response_time,
            "peak_hours": peak_hours
        }
