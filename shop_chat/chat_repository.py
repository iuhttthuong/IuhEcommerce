from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from fastapi import HTTPException
from loguru import logger
from .chat_models import ChatHistory, ChatSummary, ChatAnalytics
from models.chats import Chat, ChatMessage, ChatCreate, UpdateMessagePayload, ChatResponse, ChatMessageResponse

class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, shop_id: int, user_id: Optional[int] = None) -> Chat:
        """Create a new chat session for a specific shop"""
        if not shop_id:
            raise HTTPException(status_code=400, detail="shop_id is required")
            
        # Set customer_id to None if user_id is not provided or is 0
        customer_id = None if not user_id or user_id == 0 else user_id
            
        session = Chat(
            shop_id=shop_id,
            customer_id=customer_id,  # Use customer_id instead of user_id
            status="active",
            context={"shop_id": shop_id},
            last_message_at=datetime.now()  # Set last_message_at to current timestamp
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: int, shop_id: Optional[int] = None) -> Optional[Chat]:
        """Get chat session by ID and optionally verify shop_id"""
        query = self.db.query(Chat).filter(Chat.chat_id == session_id)
        if shop_id:
            query = query.filter(Chat.shop_id == shop_id)
        session = query.first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        return session

    def update_session(self, session_id: int, shop_id: int, status: Optional[str] = None, context: Optional[Dict] = None) -> Chat:
        """Update chat session with shop_id verification"""
        session = self.get_session(session_id, shop_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")

        if status:
            session.status = status
        if context:
            # Ensure shop_id is preserved in context
            context["shop_id"] = shop_id
            session.context = context
        session.updated_at = datetime.now()

        self.db.commit()
        self.db.refresh(session)
        return session

    def add_message(self, chat_id: int, shop_id: int, role: str, content: str, metadata: Optional[Dict] = None) -> ChatMessage:
        """Add message to chat session with shop_id verification"""
        session = self.get_session(chat_id, shop_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")

        if metadata is None:
            metadata = {}
        metadata["shop_id"] = shop_id

        message = ChatMessage(
            chat_id=chat_id,
            sender_type="user" if role == "user" else "assistant",
            sender_id=shop_id if role == "assistant" else (session.customer_id or 0),
            content=content
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_chat_history(self, session_id: int, shop_id: int, limit: int = 50) -> ChatHistory:
        """Get chat history with shop_id verification"""
        session = self.get_session(session_id, shop_id)
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
            user_id=session.customer_id,
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

    async def save_message(self, user_message: str, assistant_message: str, context: Dict[str, Any]) -> None:
        """Save a chat message to the database with shop_id verification"""
        try:
            shop_id = context.get('shop_id')
            if not shop_id:
                raise HTTPException(status_code=400, detail="shop_id is required in context")

            # Get or create chat session
            session_id = context.get('session_id')
            if not session_id:
                # Create new session if none exists
                user_id = context.get('user_id')
                # Set user_id to None if it's 0 or not provided
                if not user_id or user_id == 0:
                    user_id = None
                    
                session = self.create_session(
                    shop_id=shop_id,
                    user_id=user_id
                )
                session_id = session.chat_id
                context['session_id'] = session_id

            # Save user message
            self.add_message(
                chat_id=session_id,
                shop_id=shop_id,
                role="user",
                content=user_message,
                metadata={"context": context}
            )

            # Save assistant message
            self.add_message(
                chat_id=session_id,
                shop_id=shop_id,
                role="assistant",
                content=assistant_message,
                metadata={"context": context}
            )

            # Update session context
            self.update_session(
                session_id=session_id,
                shop_id=shop_id,
                context=context
            )

        except Exception as e:
            logger.error(f"Error saving chat message: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e)) 