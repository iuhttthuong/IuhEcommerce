from db import Session
from sqlalchemy import select, insert, func, desc
from typing import List, Dict, Any, Optional
import datetime

# Since we don't have a SearchLog model yet, we'll define a table mapping here
# You might want to create a proper model file later
from sqlalchemy import Table, Column, Integer, String, DateTime, MetaData, ForeignKey, text

metadata = MetaData()

search_logs = Table(
    'search_logs',
    metadata,
    Column('search_id', Integer, primary_key=True),
    Column('user_id', Integer, nullable=True),
    Column('customer_id', Integer, nullable=True),
    Column('search_query', String, nullable=False),
    Column('search_timestamp', DateTime, default=func.now()),
    Column('results_count', Integer, nullable=True),
    Column('clicked_product_id', Integer, nullable=True),
    Column('session_id', String, nullable=True)
)

class SearchLogRepositories:
    @staticmethod
    def create(query: str, user_id: Optional[int] = None, customer_id: Optional[int] = None, 
               results_count: Optional[int] = None, session_id: Optional[str] = None) -> int:
        """
        Log a search query
        """
        with Session() as session:
            stmt = insert(search_logs).values(
                user_id=user_id,
                customer_id=customer_id,
                search_query=query,
                search_timestamp=datetime.datetime.now(),
                results_count=results_count,
                session_id=session_id
            ).returning(search_logs.c.search_id)
            
            result = session.execute(stmt)
            session.commit()
            return result.scalar_one()
    
    @staticmethod
    def log_product_click(search_id: int, product_id: int) -> bool:
        """
        Update a search log with clicked product
        """
        with Session() as session:
            stmt = search_logs.update().\
                values(clicked_product_id=product_id).\
                where(search_logs.c.search_id == search_id)
            
            result = session.execute(stmt)
            session.commit()
            return result.rowcount > 0
    
    @staticmethod
    def get_popular_searches(limit: int = 10, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get most popular search queries from last X days
        """
        with Session() as session:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
            
            stmt = select(
                search_logs.c.search_query,
                func.count(search_logs.c.search_id).label('count')
            ).\
            where(search_logs.c.search_timestamp >= cutoff_date).\
            group_by(search_logs.c.search_query).\
            order_by(desc('count')).\
            limit(limit)
            
            result = session.execute(stmt)
            return [{"query": row.search_query, "count": row.count} for row in result]
    
    @staticmethod
    def get_user_searches(user_id: int = None, customer_id: int = None, 
                         session_id: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get search history for a specific user/customer/session
        """
        if not any([user_id, customer_id, session_id]):
            return []
            
        with Session() as session:
            stmt = select(search_logs)
            
            # Apply filters based on provided IDs
            if user_id:
                stmt = stmt.where(search_logs.c.user_id == user_id)
            if customer_id:
                stmt = stmt.where(search_logs.c.customer_id == customer_id)
            if session_id:
                stmt = stmt.where(search_logs.c.session_id == session_id)
                
            stmt = stmt.order_by(desc(search_logs.c.search_timestamp)).limit(limit)
            
            result = session.execute(stmt)
            return [dict(row._mapping) for row in result] 