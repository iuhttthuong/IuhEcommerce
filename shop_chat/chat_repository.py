from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from fastapi import HTTPException
from .chat_models import ChatMessage, ChatHistory, ChatSummary, ChatAnalytics
from models.chat import Chat, ChatCreate, UpdateChatPayload, ChatModel

class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, shop_id: int, user_id: Optional[int] = None) -> Chat:
        session = Chat(
            shop_id=shop_id,
            user_id=user_id
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: int) -> Optional[Chat]:
        return self.db.query(Chat).filter(Chat.id == session_id).first()

    def update_session(self, session_id: int, status: Optional[str] = None, context: Optional[Dict] = None) -> Chat:
        session = self.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")

        if status:
            session.status = status
        if context:
            session.context = context
        session.updated_at = datetime.now()

        self.db.commit()
        self.db.refresh(session)
        return session

    def add_message(self, chat_id: int, role: str, content: str, metadata: Optional[Dict] = None) -> ChatMessage:
        message = ChatMessage(
            chat_id=chat_id,
            role=role,
            content=content,
            metadata=metadata
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_chat_history(self, session_id: int, limit: int = 50) -> ChatHistory:
        session = self.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")

        messages = self.db.query(ChatMessage).filter(
            ChatMessage.chat_id == session_id
        ).order_by(
            ChatMessage.timestamp.asc()
        ).limit(limit).all()

        return ChatHistory(session=session, messages=messages)

    def get_chat_summary(self, session_id: int) -> ChatSummary:
        session = self.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")

        message_count = self.db.query(func.count(ChatMessage.id)).filter(
            ChatMessage.chat_id == session_id
        ).scalar()

        last_message = self.db.query(ChatMessage).filter(
            ChatMessage.chat_id == session_id
        ).order_by(
            ChatMessage.timestamp.desc()
        ).first()

        # Extract topics from messages (simplified version)
        topics = self.db.query(ChatMessage.metadata['topics'].astext).filter(
            ChatMessage.chat_id == session_id,
            ChatMessage.metadata['topics'].isnot(None)
        ).distinct().all()

        return ChatSummary(
            session_id=session_id,
            shop_id=session.shop_id,
            user_id=session.user_id,
            message_count=message_count,
            last_message=last_message.timestamp if last_message else session.created_at,
            topics=[t[0] for t in topics] if topics else [],
            sentiment=None  # You would need to implement sentiment analysis
        )

    def get_chat_analytics(self, shop_id: int, days: int = 30) -> ChatAnalytics:
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
            ChatMessage.metadata['topics'].astext,
            func.count(ChatMessage.id)
        ).filter(
            ChatMessage.chat_id.in_(
                self.db.query(Chat.id).filter(
                    Chat.shop_id == shop_id,
                    Chat.created_at >= start_date
                )
            ),
            ChatMessage.metadata['topics'].isnot(None)
        ).group_by(
            ChatMessage.metadata['topics'].astext
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

        return ChatAnalytics(
            total_sessions=total_sessions,
            active_sessions=active_sessions,
            average_messages_per_session=avg_messages,
            common_topics=[{"topic": t[0], "count": t[1]} for t in common_topics],
            average_response_time=avg_response_time,
            satisfaction_score=None,  # You would need to implement satisfaction scoring
            peak_hours=peak_hours
        ) 