import sys
import uuid
from concurrent.futures import ThreadPoolExecutor
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from env import env
from embedding.generate_embeddings import generate_embedding
from embedding.process import (
    preprocess_product,
    preprocess_faq,
    preprocess_review,
    preprocess_category,
    preprocess_chat,
    preprocess_search_log
)
from db import Session
from models.products import Product
from models.fqas import FQA
from models.chats import Chat
from models.categories import Category
from models.reviews import Review
from repositories.products import ProductRepositories
from repositories.fqas import FQARepositories
from repositories.categories import CategoryRepositories
from repositories.chat import ChatRepository
from repositories.message import MessageRepository
from repositories.reviews import ReviewRepositories
from repositories.search_logs import SearchLogRepositories
from loguru import logger

# Định nghĩa các collection
COLLECTIONS = {
    "products": "product_embeddings",
    "faqs": "faq_embeddings",
    "reviews": "review_embeddings",
    "categories": "category_embeddings",
    "chats": "chat_embeddings",
    "search_logs": "search_log_embeddings",
}

# Kết nối Qdrant với xử lý lỗi
try:
    qdrant_url = f"http://localhost:{env.QD_PORT}"
    logger.info(f"Connecting to Qdrant at {qdrant_url}")
    qdrant = QdrantClient(qdrant_url)
    # Test connection
    qdrant.get_collections()
    logger.info("Successfully connected to Qdrant")
except Exception as e:
    logger.error(f"Failed to connect to Qdrant: {e}")
    # Fallback to default port
    qdrant_url = "http://localhost:6333"
    logger.warning(f"Falling back to default Qdrant URL: {qdrant_url}")
    qdrant = QdrantClient(qdrant_url)

def ensure_collections_exist():
    """Đảm bảo các collection tồn tại trong Qdrant"""
    try:
        collections = qdrant.get_collections().collections
        collection_names = [col.name for col in collections]
        logger.info(f"Found existing collections: {collection_names}")

        for collection_type, collection_name in COLLECTIONS.items():
            if (collection_name not in collection_names):
                logger.info(f"Creating collection: {collection_name}")
                qdrant.create_collection(
                    collection_name=collection_name,
                    vectors_config={"default": VectorParams(
                        size=3072,
                        distance=Distance.COSINE,
                        on_disk=True  # Store vectors on disk to save memory
                    )},
                    on_disk_payload=True  # Store payload on disk
                )
                logger.info(f"✅ Created collection: {collection_name}")
            else:
                logger.info(f"ℹ️ Collection exists: {collection_name}")
    except Exception as e:
        logger.error(f"Error ensuring collections exist: {e}")
        raise

def add_product_to_qdrant(product_id: int):
    """Thêm thông tin sản phẩm vào Qdrant"""
    try:
        product_info = ProductRepositories.get_info(product_id)
        product_data = preprocess_product(product_info)
        embedding = generate_embedding(product_data)
        product = product_info.get("product", {})
        if embedding:
            point = PointStruct(
                id=product_id,
                vector=embedding,
                payload={
                    "product_id": product_id,
                    "name": product.name,
                    "short_description": product.short_description,
                    "price": product.price,
                    "category_id": product.category_id,
                    "brand_id": product.brand_id,
                    "seller_id": product.seller_id,
                    "rating_average": product.rating_average,
                    "text_content": product_data,
                    "embedding_type": "product"
                },
                vector_name="default"
            )
            qdrant.upsert(collection_name=COLLECTIONS["products"], points=[point])
            print(f"✅ Đã thêm embedding cho sản phẩm ID {product_id}.")
        else:
            print(f"❌ Không thể tạo embedding cho sản phẩm ID {product_id}.")

    except Exception as e:
        print(f"⚠️ Lỗi khi xử lý sản phẩm ID {product_id}: {e}")

def add_faq_to_qdrant(faq_id: int):
    """Thêm thông tin FAQ vào Qdrant"""
    try:
        faq_info = FQARepositories.get_by_id(faq_id)
        if not faq_info:
            print(f"⚠️ Không tìm thấy FAQ với ID: {faq_id}")
            return
            
        faq_data = preprocess_faq(faq_info)
        embedding = generate_embedding(faq_data)
        
        if embedding:
            # Truy cập thuộc tính trực tiếp từ đối tượng FQAModel
            question = faq_info.question if hasattr(faq_info, 'question') else ""
            answer = faq_info.answer if hasattr(faq_info, 'answer') else ""
            
            point = PointStruct(
                id=faq_id,
                vector=embedding,
                payload={
                    "faq_id": faq_id,
                    "question": question,
                    "answer": answer,
                    "text_content": faq_data,
                    "embedding_type": "faq"
                },
                vector_name="default"
            )
            qdrant.upsert(collection_name=COLLECTIONS["faqs"], points=[point])
            print(f"✅ Đã thêm embedding cho FAQ ID {faq_id}.")
        else:
            print(f"❌ Không thể tạo embedding cho FAQ ID {faq_id}.")

    except Exception as e:
        print(f"⚠️ Lỗi khi xử lý FAQ ID {faq_id}: {e}")

def add_review_to_qdrant(review_id: int):
    """Thêm thông tin đánh giá vào Qdrant"""
    try:
        review_info = ReviewRepositories.get_by_id(review_id)
        review_data = preprocess_review(review_info)
        embedding = generate_embedding(review_data)
        
        if embedding:
            point = PointStruct(
                id=review_id,
                vector=embedding,
                payload={
                    "review_id": review_id,
                    "product_id": review_info.get("product_id", ""),
                    "customer_id": review_info.get("customer_id", ""),
                    "rating": review_info.get("rating", 0),
                    "comment": review_info.get("comment", ""),
                    "text_content": review_data,
                    "embedding_type": "review"
                },
                vector_name="default"
            )
            qdrant.upsert(collection_name=COLLECTIONS["reviews"], points=[point])
            print(f"✅ Đã thêm embedding cho Review ID {review_id}.")
        else:
            print(f"❌ Không thể tạo embedding cho Review ID {review_id}.")

    except Exception as e:
        print(f"⚠️ Lỗi khi xử lý Review ID {review_id}: {e}")

def add_category_to_qdrant(category_id: int):
    """Thêm thông tin danh mục vào Qdrant"""
    try:
        category_info = CategoryRepositories.get_by_id(category_id)
        if not category_info:
            print(f"⚠️ Không tìm thấy Category với ID: {category_id}")
            return
            
        category_data = preprocess_category(category_info)
        embedding = generate_embedding(category_data)
        
        if embedding:
            # Truy cập thuộc tính trực tiếp từ đối tượng Category
            name = category_info.name if hasattr(category_info, 'name') else ""
            path = category_info.path if hasattr(category_info, 'path') else ""
            
            # Đảm bảo ID là hợp lệ cho Qdrant
            from embedding.run_embedding import convert_category_id_for_qdrant
            str_id = str(category_id)
            if "/" in str_id:
                # Chuyển đổi ID phức tạp thành số nguyên đơn giản
                qdrant_id = convert_category_id_for_qdrant(str_id)
            else:
                try:
                    qdrant_id = int(category_id)
                except (ValueError, TypeError):
                    import hashlib
                    # Tạo hash từ chuỗi id ban đầu để làm id cho Qdrant
                    qdrant_id = int(hashlib.md5(str(category_id).encode()).hexdigest(), 16) % (2**31)
            
            point = PointStruct(
                id=qdrant_id,
                vector=embedding,
                payload={
                    "category_id": str(category_id),  # Lưu ID gốc dưới dạng chuỗi
                    "name": name,
                    "path": path,
                    "text_content": category_data,
                    "embedding_type": "category"
                },
                vector_name="default"
            )
            qdrant.upsert(collection_name=COLLECTIONS["categories"], points=[point])
            print(f"✅ Đã thêm embedding cho Category ID {category_id}.")
        else:
            print(f"❌ Không thể tạo embedding cho Category ID {category_id}.")

    except Exception as e:
        print(f"⚠️ Lỗi khi xử lý Category ID {category_id}: {e}")

def add_chat_to_qdrant(chat_id: int):
    """Thêm thông tin chat vào Qdrant"""
    try:
        chat_info = ChatRepository.get_one(chat_id)
        if not chat_info:
            print(f"⚠️ Không tìm thấy Chat với ID: {chat_id}")
            return
        
        # Lấy tin nhắn từ MessageRepository
        try:
            messages = MessageRepository.get_recent_messages(chat_id, limit=20)
            # Chuyển đổi đối tượng message thành dictionary
            message_data = []
            for msg in messages:
                message_data.append({
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at
                })
        except Exception as e:
            print(f"⚠️ Lỗi khi lấy tin nhắn cho Chat ID {chat_id}: {e}")
            message_data = []
            
        # Xây dựng đối tượng chat phù hợp nếu không có thuộc tính get
        chat_data = {
            "id": chat_info.id,
            "session_id": chat_info.session_id,
            "user_id": chat_info.user_id,
            "title": chat_info.title,
            "messages": message_data  # Thêm tin nhắn vào dữ liệu chat
        }
        
        chat_data_text = preprocess_chat(chat_data)
        embedding = generate_embedding(chat_data_text)
        
        if embedding:
            point = PointStruct(
                id=chat_id,
                vector=embedding,
                payload={
                    "chat_id": chat_id,
                    "session_id": chat_info.session_id,
                    "user_id": chat_info.user_id,
                    "title": chat_info.title or "",  # Use empty string if title is None
                    "message_count": len(message_data),  # Thêm số lượng tin nhắn
                    "text_content": chat_data_text,
                    "embedding_type": "chat"
                },
                vector_name="default"
            )
            qdrant.upsert(collection_name=COLLECTIONS["chats"], points=[point])
            print(f"✅ Đã thêm embedding cho Chat ID {chat_id} với {len(message_data)} tin nhắn.")
        else:
            print(f"❌ Không thể tạo embedding cho Chat ID {chat_id}.")

    except Exception as e:
        print(f"⚠️ Lỗi khi xử lý Chat ID {chat_id}: {e}")

def embed_and_upsert_to_qdrant(data: dict, text_content: str, topic: str):
    """
    Tạo embedding và lưu vào Qdrant cho dữ liệu từ Kafka CDC
    
    Args:
        data: Dict chứa dữ liệu gốc từ Kafka
        text_content: Văn bản đã được tiền xử lý
        topic: Tên topic Kafka, dùng để xác định loại dữ liệu
    """
    try:
        # Tạo embedding từ text đã xử lý
        embedding = generate_embedding(text_content)
        if not embedding:
            print(f"❌ Không thể tạo embedding cho dữ liệu từ topic {topic}")
            return

        # Xác định collection dựa vào topic
        collection_type = topic.split('.')[-1]  # Lấy phần cuối của topic (products, fqas, etc.)
        collection_name = COLLECTIONS.get(collection_type)
        if not collection_name:
            print(f"❌ Không tìm thấy collection cho topic {topic}")
            return

        # Tạo payload tùy theo loại dữ liệu
        payload = {
            "text_content": text_content,
            "embedding_type": collection_type,
            **data  # Thêm toàn bộ dữ liệu gốc vào payload
        }

        # Tạo point để lưu vào Qdrant
        point = PointStruct(
            id=data.get('id') or str(uuid.uuid4()),  # Sử dụng ID từ dữ liệu hoặc tạo mới
            vector=embedding,
            payload=payload,
            vector_name="default"
        )

        # Upsert vào Qdrant
        qdrant.upsert(collection_name=collection_name, points=[point])
        print(f"✅ Đã thêm embedding cho {collection_type} ID {point.id}")

    except Exception as e:
        print(f"⚠️ Lỗi khi xử lý dữ liệu từ {topic}: {e}")

def process_all_data():
    """Xử lý tất cả dữ liệu và tạo embedding cho từng loại"""
    with Session() as session:
        # Process products
        products = session.query(Product).all()
        with ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(lambda product: add_product_to_qdrant(product.product_id), products)
        
        # Process FAQs
        faqs = session.query(FQA).all()
        with ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(lambda faq: add_faq_to_qdrant(faq.id), faqs)
        
        # Process categories
        categories = session.query(Category).all()
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Đảm bảo category_id là integer
            executor.map(lambda category: add_category_to_qdrant(int(category.category_id)), categories)
        
        # Process reviews
        reviews = session.query(Review).all()
        with ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(lambda review: add_review_to_qdrant(review.review_id), reviews)
        
        # Process chats
        chats = session.query(Chat).all()
        with ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(lambda chat: add_chat_to_qdrant(chat.id), chats)
    
    print("🎉 Đã hoàn tất việc thêm embeddings vào Qdrant.")

def main():
    ensure_collections_exist()
    process_all_data()

if __name__ == "__main__":
    main()
