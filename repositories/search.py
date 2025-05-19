from env import env
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from embedding.generate_embeddings import query_embedding, generate_embedding
from models.products import Product, ProductResponse, ProductCreate
from db import Session
from repositories.products import ProductRepositories
from embedding.main import COLLECTIONS
from loguru import logger
from typing import List, Dict, Any
import json
from difflib import SequenceMatcher
import requests

# Initialize Qdrant client with fallback URL
try:
    qdrant_url = getattr(env, 'QDRANT_URL', 'http://localhost:6333')
    qdrant = QdrantClient(qdrant_url)
    logger.info(f"Initialized Qdrant client with URL: {qdrant_url}")
except Exception as e:
    logger.error(f"Failed to initialize Qdrant client: {e}")
    qdrant = QdrantClient("http://localhost:6333")
    logger.warning("Using default Qdrant URL: http://localhost:6333")

def init_collections():
    """Initialize Qdrant collections if they don't exist."""
    try:
        collections = qdrant.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        # Create products collection if it doesn't exist
        if "products" not in collection_names:
            qdrant.create_collection(
                collection_name="product_embeddings",
                vectors_config={
                    "default": qdrant_models.VectorParams(
                        size=3072,  # OpenAI embedding dimension
                        distance=qdrant_models.Distance.COSINE,
                        on_disk=True,  # Store vectors on disk to save memory
                        hnsw_config=qdrant_models.HnswConfig(
                            m=16,  # Number of connections per element
                            ef_construct=100,  # Size of the dynamic candidate list
                            full_scan_threshold=10000,  # Use HNSW for collections smaller than this
                            max_indexing_threads=4,  # Number of threads for index building
                            on_disk=True  # Store index on disk
                        )
                    )
                }
            )
            logger.info("Created collection: products with HNSW index")
            
        # Create categories collection if it doesn't exist
        if "categories" not in collection_names:
            qdrant.create_collection(
                collection_name="category_embeddings",
                vectors_config=qdrant_models.VectorParams(
                    size=3072,  # OpenAI embedding dimension
                    distance=qdrant_models.Distance.COSINE,
                    on_disk=True,  # Store vectors on disk to save memory
                    hnsw_config=qdrant_models.HnswConfig(
                        m=16,
                        ef_construct=100,
                        full_scan_threshold=10000,
                        max_indexing_threads=4,
                        on_disk=True
                    )
                )
            )
            logger.info("Created collection: categories with HNSW index")
            
    except Exception as e:
        logger.error(f"Error initializing collections: {e}")
        raise  # Re-raise the exception to ensure the application knows about the failure

# Initialize collections on module import
init_collections()

class SearchRepository:
    @staticmethod
    def semantic_search( query: str, collection_name: str = "product_embeddings", limit: int = 5):
        print("❤️❤️❤️❤️❤️query:", query)
        """
        Vector search sản phẩm trên Qdrant (chuẩn, có vector_name).
        Args:
            query (str): Chuỗi truy vấn tìm kiếm.
            limit (int): Số kết quả trả về tối đa.
            score_threshold (float): Ngưỡng điểm tương đồng tối thiểu.
        Returns:
            List[dict]: Danh sách sản phẩm phù hợp.
        """
        # try:
        #     query_vector = generate_embedding(query)
        #     if query_vector is None:
        #         logger.error("Không tạo được embedding cho truy vấn")
        #         return []

            # search_result = qdrant.search(
            #     collection_name=collection_name,
            #     query_vector=query_vector,
            #     limit=limit,
            #     score_threshold=score_threshold,
            #     with_payload=True,
            #     search_params=qdrant_models.SearchParams(
            #         hnsw_ef=128,
            #         exact=False
            #     )
            # )
        search_result = qdrant.query_points(
            collection_name=collection_name,
            query = generate_embedding(query),
            using = "default",
            limit=limit,
            with_payload=True,
            with_vectors=False
        )

            # results = []
            # for hit in search_result:
            #     if hit.score >= 0.7:
            #         product_info = ProductRepositories.get_info(hit.id)
            #         if product_info and product_info.get("product"):
            #             product = product_info["product"]
            #             results.append({
            #                 "id": hit.id,
            #                 "score": hit.score,
            #                 "name": product.name,
            #                 "description": product.description,
            #                 "price": product.price,
            #             })
        return search_result

        # except Exception as e:
        #     logger.error(f"Lỗi khi vector search: {e}")
        #     return []

    @staticmethod
    def upsert_product(product_id: int, product_name: str, description: str, category: str = None):
        """Upsert a product into the search index."""
        try:
            # Generate embedding for product name and description
            text = f"{product_name} {description}"
            vector = generate_embedding(text)
            if vector is None:
                logger.error(f"Failed to generate embedding for product {product_id}")
                return False

            # Prepare payload
            payload = {
                "product_id": product_id,
                "product_name": product_name,
                "description": description
            }
            if category:
                payload["category"] = category

            # Upsert to Qdrant
            qdrant.upsert(
                collection_name="product_embeddings",
                points=[
                    qdrant_models.PointStruct(
                        id=product_id,
                        vector=vector,
                        payload=payload,
                        vector_name="default"
                    )
                ]
            )
            logger.info(f"Successfully upserted product {product_id}")
            return True

        except Exception as e:
            logger.error(f"Error upserting product {product_id}: {e}")
            return False

    @staticmethod
    def delete_product(product_id: int):
        """Delete a product from the search index."""
        try:
            qdrant.delete(
                collection_name="product_embeddings",
                points_selector=qdrant_models.PointIdsList(
                    points=[product_id]
                )
            )
            logger.info(f"Successfully deleted product {product_id} from search index")
            return True
        except Exception as e:
            logger.error(f"Error deleting product {product_id} from search index: {e}")
            return False

