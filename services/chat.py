from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from fastapi import HTTPException
from models.chats import (
    Chat, ChatMessage,
    ChatCreate, ChatMessageCreate, ChatResponse, ChatMessageResponse
)
from models.shops import Shop
from models.customers import Customer
import json

class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, data: ChatCreate) -> Chat:
        # Create new chat session
        chat = Chat(
            shop_id=data.shop_id,
            customer_id=data.customer_id,
            status="active",
            last_message_at=datetime.utcnow()
        )
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def get_session(self, chat_id: int) -> Chat:
        return self.db.query(Chat).filter(Chat.chat_id == chat_id).first()

    def add_message(self, data: ChatMessageCreate) -> ChatMessage:
        message = ChatMessage(
            chat_id=data.chat_id,
            sender_type=data.sender_type,
            sender_id=data.sender_id,
            content=data.content,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(message)
        
        # Update last_message_at in chat
        chat = self.get_session(data.chat_id)
        if chat:
            chat.last_message_at = message.created_at or datetime.utcnow()
            self.db.add(chat)
        
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_messages(self, chat_id: int) -> List[ChatMessage]:
        return self.db.query(ChatMessage).filter(
            ChatMessage.chat_id == chat_id
        ).order_by(
            ChatMessage.created_at.asc()
        ).all()

    def get_chat_by_customer_id(self, customer_id: int) -> List[Chat]:
        return self.db.query(Chat).filter(
            Chat.customer_id == customer_id
        ).order_by(
            Chat.last_message_at.desc()
        ).all()

    def get_chat_by_shop_id(self, shop_id: int) -> List[Chat]:
        return self.db.query(Chat).filter(
            Chat.shop_id == shop_id
        ).order_by(
            Chat.last_message_at.desc()
        ).all()

    def get_active_sessions(self, shop_id: int) -> List[Chat]:
        return self.db.query(Chat).filter(
            Chat.shop_id == shop_id,
            Chat.status == "active"
        ).all()

    def close_session(self, chat_id: int) -> Chat:
        chat = self.get_session(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        chat.status = "closed"
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def get_session_summary(self, chat_id: int) -> Dict[str, Any]:
        chat = self.get_session(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat session not found")

        messages = self.get_messages(chat_id)
        return {
            "chat_id": chat.chat_id,
            "shop_id": chat.shop_id,
            "customer_id": chat.customer_id,
            "message_count": len(messages),
            "last_message": messages[-1].timestamp if messages else chat.last_message_at,
            "status": chat.status,
            "created_at": chat.created_at,
            "updated_at": chat.updated_at
        }

    def get_shop_chat_analytics(self, shop_id: int, days: int = 30) -> Dict[str, Any]:
        start_date = datetime.utcnow() - timedelta(days=days)

        # Get total and active sessions
        total_sessions = self.db.query(func.count(Chat.chat_id)).filter(
            Chat.shop_id == shop_id,
            Chat.created_at >= start_date
        ).scalar()

        active_sessions = self.db.query(func.count(Chat.chat_id)).filter(
            Chat.shop_id == shop_id,
            Chat.status == "active",
            Chat.updated_at >= start_date
        ).scalar()

        # Get average messages per session
        total_messages = self.db.query(func.count(ChatMessage.message_id)).filter(
            ChatMessage.chat_id.in_(
                self.db.query(Chat.chat_id).filter(
                    Chat.shop_id == shop_id,
                    Chat.created_at >= start_date
                )
            )
        ).scalar()

        avg_messages = total_messages / total_sessions if total_sessions > 0 else 0

        # Get average response time
        response_times = []
        messages = self.db.query(ChatMessage).filter(
            ChatMessage.chat_id.in_(
                self.db.query(Chat.chat_id).filter(
                    Chat.shop_id == shop_id,
                    Chat.created_at >= start_date
                )
            )
        ).order_by(
            ChatMessage.chat_id,
            ChatMessage.timestamp
        ).all()

        for i in range(1, len(messages)):
            if messages[i].sender_type == "shop" and messages[i-1].sender_type == "customer":
                response_time = (messages[i].timestamp - messages[i-1].timestamp).total_seconds()
                response_times.append(response_time)

        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        # Get peak hours
        peak_hours = {}
        for hour in range(24):
            count = self.db.query(func.count(ChatMessage.message_id)).filter(
                ChatMessage.chat_id.in_(
                    self.db.query(Chat.chat_id).filter(
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
            "average_response_time": avg_response_time,
            "peak_hours": peak_hours
        }
