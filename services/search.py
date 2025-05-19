from qdrant_client import QdrantClient
from env import env
from embedding.generate_embeddings import query_embedding
from repositories.search import SearchRepository
import json
from loguru import logger
from typing import Dict, List, Optional, Any

from embedding.main import COLLECTIONS

class SearchServices:
    @staticmethod
    def search(query : str, collection_name: str = "product_embeddings", limit: int = 5) -> List[Dict[str, Any]]:
        """Search for products using semantic search."""
        try:
            # Perform semantic search
            results = SearchRepository.semantic_search(
                query=query ,
                limit=limit,
                collection_name=collection_name
            )
            
            if not results:
                logger.warning(f"No results found for query: {query }")
                return []

            return results
            
        except Exception as e:
            logger.error(f"Error in search service: {e}")
            return []

    @staticmethod
    def index_product(product_id: int, product_name: str, description: str, category: str = None) -> bool:
        """Index a product for search."""
        try:
            return SearchRepository.upsert_product(
                product_id=product_id,
                product_name=product_name,
                description=description,
                category=category
            )
        except Exception as e:
            logger.error(f"Error indexing product {product_id}: {e}")
            return False

    @staticmethod
    def remove_product(product_id: int) -> bool:
        """Remove a product from search index."""
        try:
            return SearchRepository.delete_product(product_id)
        except Exception as e:
            logger.error(f"Error removing product {product_id} from index: {e}")
            return False