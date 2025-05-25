from env import env
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from embedding.generate_embeddings import generate_embedding
from loguru import logger
from typing import List, Dict, Any
import json

# Initialize Qdrant client with fallback URL
try:
    qdrant_url = getattr(env, 'QDRANT_URL', 'http://localhost:6333')
    qdrant = QdrantClient(qdrant_url)
    logger.info(f"Initialized Qdrant client with URL: {qdrant_url}")
except Exception as e:
    logger.error(f"Failed to initialize Qdrant client: {e}")
    qdrant = QdrantClient("http://localhost:6333")
    logger.warning("Using default Qdrant URL: http://localhost:6333")

def init_comparison_collection():
    """Initialize Qdrant collection for product comparisons if it doesn't exist."""
    try:
        collections = qdrant.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        # Create product comparison collection if it doesn't exist
        if "product_comparison_embeddings" not in collection_names:
            qdrant.create_collection(
                collection_name="product_comparison_embeddings",
                vectors_config={
                    "default": qdrant_models.VectorParams(
                        size=3072,  # OpenAI embedding dimension
                        distance=qdrant_models.Distance.COSINE,
                        on_disk=True,  # Store vectors on disk to save memory
                        hnsw_config=qdrant_models.HnswConfigDiff(
                            m=16,  # Number of connections per element
                            ef_construct=100,  # Size of the dynamic candidate list
                            full_scan_threshold=10000,  # Use HNSW for collections smaller than this
                            max_indexing_threads=4,  # Number of threads for index building
                            on_disk=True  # Store index on disk
                        )
                    )
                }
            )
            logger.info("Created collection: product_comparison_embeddings with HNSW index")
            
    except Exception as e:
        logger.error(f"Error initializing comparison collection: {e}")
        raise  # Re-raise the exception to ensure the application knows about the failure

# Initialize collection on module import
init_comparison_collection()

class SearchCompareRepository:
    @staticmethod
    def semantic_search(query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Vector search sản phẩm cho mục đích so sánh.
        Args:
            query (str): Chuỗi truy vấn tìm kiếm.
            limit (int): Số kết quả trả về tối đa.
        Returns:
            List[dict]: Danh sách sản phẩm phù hợp.
        """
        try:
            query_vector = generate_embedding(query)
            if query_vector is None:
                logger.error("Không tạo được embedding cho truy vấn")
                return []

            search_result = qdrant.query_points(
                collection_name="product_comparison_embeddings",
                query=query_vector,
                using="default",
                limit=limit,
                with_payload=True,
                with_vectors=False
            )

            # Chuyển đổi kết quả từ QueryResponse thành list
            results = []
            for point in search_result.points:
                if point.score >= 0.7:  # Chỉ lấy kết quả có độ tương đồng cao
                    results.append({
                        "id": point.id,
                        "score": point.score,
                        "payload": point.payload
                    })

            return results

        except Exception as e:
            logger.error(f"Lỗi khi vector search cho so sánh: {e}")
            return []

    @staticmethod
    def upsert_product_for_comparison(product_id: int, product_name: str, description: str, specifications: Dict[str, Any] = None) -> bool:
        """
        Thêm hoặc cập nhật sản phẩm vào index so sánh.
        Args:
            product_id (int): ID sản phẩm
            product_name (str): Tên sản phẩm
            description (str): Mô tả sản phẩm
            specifications (Dict[str, Any]): Thông số kỹ thuật
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            # Tạo embedding từ tên và mô tả sản phẩm
            text = f"{product_name} {description}"
            if specifications:
                # Thêm thông số kỹ thuật vào text để tạo embedding
                specs_text = " ".join([f"{k}: {v}" for k, v in specifications.items()])
                text += f" {specs_text}"
                
            vector = generate_embedding(text)
            if vector is None:
                logger.error(f"Không tạo được embedding cho sản phẩm {product_id}")
                return False

            # Chuẩn bị payload
            payload = {
                "product_id": product_id,
                "product_name": product_name,
                "description": description
            }
            if specifications:
                payload["specifications"] = specifications

            # Upsert vào Qdrant
            qdrant.upsert(
                collection_name="product_comparison_embeddings",
                points=[
                    qdrant_models.PointStruct(
                        id=product_id,
                        vector=vector,
                        payload=payload,
                        vector_name="default"
                    )
                ]
            )
            logger.info(f"Đã thêm/cập nhật sản phẩm {product_id} vào index so sánh")
            return True

        except Exception as e:
            logger.error(f"Lỗi khi thêm/cập nhật sản phẩm {product_id} vào index so sánh: {e}")
            return False

    @staticmethod
    def delete_product_from_comparison(product_id: int) -> bool:
        """
        Xóa sản phẩm khỏi index so sánh.
        Args:
            product_id (int): ID sản phẩm cần xóa
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            qdrant.delete(
                collection_name="product_comparison_embeddings",
                points_selector=qdrant_models.PointIdsList(
                    points=[product_id]
                )
            )
            logger.info(f"Đã xóa sản phẩm {product_id} khỏi index so sánh")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi xóa sản phẩm {product_id} khỏi index so sánh: {e}")
            return False

    @staticmethod
    def find_similar_products(product_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Tìm các sản phẩm tương tự dựa trên ID sản phẩm.
        Args:
            product_id (int): ID sản phẩm cần tìm tương tự
            limit (int): Số lượng kết quả tối đa
        Returns:
            List[Dict[str, Any]]: Danh sách sản phẩm tương tự
        """
        try:
            # Lấy vector của sản phẩm gốc
            point = qdrant.retrieve(
                collection_name="product_comparison_embeddings",
                ids=[product_id],
                with_vectors=True
            )
            
            if not point:
                logger.error(f"Không tìm thấy sản phẩm {product_id}")
                return []
                
            # Tìm kiếm các sản phẩm tương tự
            search_result = qdrant.query_points(
                collection_name="product_comparison_embeddings",
                query=point[0].vector,
                using="default",
                limit=limit + 1,  # +1 để loại bỏ sản phẩm gốc
                with_payload=True,
                with_vectors=False
            )
            
            # Lọc kết quả và loại bỏ sản phẩm gốc
            results = []
            for point in search_result.points:
                if point.id != product_id and point.score >= 0.7:
                    results.append({
                        "id": point.id,
                        "score": point.score,
                        "payload": point.payload
                    })
                    
            return results[:limit]  # Giới hạn số lượng kết quả
            
        except Exception as e:
            logger.error(f"Lỗi khi tìm sản phẩm tương tự cho {product_id}: {e}")
            return []
