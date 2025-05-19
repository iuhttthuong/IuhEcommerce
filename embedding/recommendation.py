import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from env import env
from embedding.generate_embeddings import query_embedding
from embedding.main import COLLECTIONS
from typing import List, Dict, Any, Optional, Union
from loguru import logger

# Kết nối Qdrant
qdrant = QdrantClient(f"http://localhost:{env.QD_PORT}")

def get_similar_products(product_id: int, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get similar products based on a given product ID
    """
    try:
        # Get product vector from Qdrant
        product_vector = qdrant.get_points(
            collection_name=COLLECTIONS["products"],
            ids=[product_id],
            with_payload=False,
            with_vectors=True
        )
        
        # Check if product exists and has vector
        if not product_vector.points or "vectors" not in product_vector.points[0]:
            logger.warning(f"Product ID {product_id} not found or has no vector")
            return []
        
        # Get product vector
        vector = product_vector.points[0].vectors.get("default")
        
        # Search similar products
        similar_products = qdrant.search(
            collection_name=COLLECTIONS["products"],
            query_vector={"default": vector},
            limit=limit + 1,  # Get one more to exclude the original product
            with_payload=True
        )
        
        # Filter out the original product and convert to dict format
        recommendations = []
        for product in similar_products:
            if product.id != product_id:  # Exclude original product
                recommendations.append({
                    "product_id": product.id,
                    "score": product.score,
                    "name": product.payload.get("name", ""),
                    "price": product.payload.get("price", 0),
                    "short_description": product.payload.get("short_description", ""),
                    "rating_average": product.payload.get("rating_average", 0)
                })
        
        return recommendations[:limit]  # Ensure we only return the requested number
    
    except Exception as e:
        logger.error(f"Error getting similar products: {e}")
        return []

def get_category_recommendations(category_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Tìm các sản phẩm hàng đầu trong một danh mục
    """
    try:
        # Lọc sản phẩm theo category_id
        search_result = qdrant.scroll(
            collection_name=COLLECTIONS["products"],
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="category_id",
                        match=MatchValue(value=category_id)
                    )
                ]
            ),
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )[0]
        
        # Chuyển đổi kết quả sang định dạng đơn giản hơn
        recommendations = []
        for product in search_result:
            recommendations.append({
                "product_id": product.id,
                "name": product.payload.get("name", ""),
                "price": product.payload.get("price", 0),
                "short_description": product.payload.get("short_description", ""),
                "rating_average": product.payload.get("rating_average", 0),
            })
        
        return recommendations
    
    except Exception as e:
        print(f"⚠️ Lỗi khi tìm sản phẩm trong danh mục: {e}")
        return []

def get_text_based_recommendations(query_text: str, limit: int = 5, score_threshold: float = 0.7) -> List[Dict[str, Any]]:
    """
    Get product recommendations based on text query
    """
    try:
        # Normalize query - remove special characters and normalize case
        query_text = query_text.lower().strip()
        
        # Generate query embedding
        query_vector = query_embedding(query_text)
        
        # Search for relevant products with lower threshold to catch more matches
        product_results = qdrant.search(
            collection_name=COLLECTIONS["products"],
            query_vector={"default": query_vector},
            limit=limit + 5,  # Get more results to filter by relevance
            with_payload=True,
            score_threshold=score_threshold  # Use the provided threshold
        )
        
        # Convert to dict format with additional processing
        recommendations = []
        
        # Keep track of seen product names to avoid duplicates
        seen_product_names = set()
        
        for product in product_results:
            product_name = product.payload.get("name", "")
            if product_name not in seen_product_names:
                seen_product_names.add(product_name)
                recommendations.append({
                    "product_id": product.id,
                    "score": product.score,
                    "name": product_name,
                    "price": product.payload.get("price", 0),
                    "short_description": product.payload.get("short_description", ""),
                    "rating_average": product.payload.get("rating_average", 0),
                    "category_id": product.payload.get("category_id", ""),
                    "brand_id": product.payload.get("brand_id", 0),
                    "seller_id": product.payload.get("seller_id", 0)
                })
                
        # Sort by score and trim to requested limit
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:limit]
    
    except Exception as e:
        logger.error(f"Error getting text-based recommendations: {e}")
        return []

def get_personalized_recommendations(customer_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Tạo gợi ý sản phẩm cá nhân hóa dựa trên lịch sử mua hàng và tìm kiếm của khách hàng
    """
    try:
        # Placeholder cho dữ liệu mô tả người dùng (cần triển khai)
        # Trong thực tế, bạn sẽ truy vấn cơ sở dữ liệu để lấy lịch sử mua hàng, xem, tìm kiếm
        # và tạo một biểu diễn vector cho người dùng
        
        # Ví dụ: Lấy top sản phẩm dựa trên rating trung bình
        top_products = qdrant.search(
            collection_name=COLLECTIONS["products"],
            query_vector=None,  # Không sử dụng vector, chỉ dựa vào score
            limit=limit,
            with_payload=True,
            with_vectors=False,
            score_threshold=0.0,
            append_payload=True,
        )
        
        # Chuyển đổi kết quả sang định dạng đơn giản hơn
        recommendations = []
        for product in top_products:
            recommendations.append({
                "product_id": product.id,
                "score": product.payload.get("rating_average", 0),
                "name": product.payload.get("name", ""),
                "price": product.payload.get("price", 0),
                "short_description": product.payload.get("short_description", ""),
                "rating_average": product.payload.get("rating_average", 0),
            })
        
        # Sắp xếp theo rating_average giảm dần
        recommendations.sort(key=lambda x: x["rating_average"], reverse=True)
        
        return recommendations[:limit]
    
    except Exception as e:
        print(f"⚠️ Lỗi khi tạo gợi ý cá nhân hóa: {e}")
        return [] 