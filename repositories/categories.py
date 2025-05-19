from db import Session
from models.categories import Category
from sqlalchemy import select
from typing import List, Optional, Dict, Any

class CategoryRepositories:
    @staticmethod
    def get_all() -> List[Category]:
        with Session() as session:
            query = select(Category)
            result = session.execute(query).scalars().all()
            return result
    
    @staticmethod
    def get_by_id(category_id: int) -> Optional[Category]:
        with Session() as session:
            query = select(Category).where(Category.category_id == category_id)
            result = session.execute(query).scalar_one_or_none()
            return result
    
    @staticmethod
    def get_categories_by_path_prefix(path_prefix: str) -> List[Category]:
        """
        Get categories where path starts with the given prefix
        Useful for finding subcategories
        """
        with Session() as session:
            query = select(Category).where(Category.path.like(f"{path_prefix}%"))
            result = session.execute(query).scalars().all()
            return result
    
    @staticmethod
    def get_category_tree() -> List[Dict[str, Any]]:
        """
        Returns a flat list of all categories with their paths
        The path structure can be used to rebuild the hierarchy if needed
        """
        with Session() as session:
            query = select(Category)
            all_categories = session.execute(query).scalars().all()
            
            result = []
            for cat in all_categories:
                category_data = {
                    "category_id": cat.category_id,
                    "name": cat.name,
                    "path": cat.path
                }
                result.append(category_data)
            
            return result 