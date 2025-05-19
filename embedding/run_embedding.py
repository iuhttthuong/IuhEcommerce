#!/usr/bin/env python
"""
Script để chạy quá trình tạo embedding cho tất cả các collections
"""

import time
import argparse
from loguru import logger
from embedding.main import (
    ensure_collections_exist,
    process_all_data,
    add_product_to_qdrant,
    add_faq_to_qdrant,
    add_review_to_qdrant,
    add_category_to_qdrant,
    add_chat_to_qdrant,
    COLLECTIONS,
    qdrant
)
from db import Session
from models import Product, FQA, Review, Category, Chat, User  # Import from models package
from models.user import User


def check_item_exists_in_qdrant(collection_name, item_id):
    """
    Kiểm tra xem một item đã tồn tại trong Qdrant chưa
    
    Args:
        collection_name: Tên collection trong Qdrant
        item_id: ID của item cần kiểm tra
        
    Returns:
        bool: True nếu item đã tồn tại, False nếu chưa
    """
    try:
        # Xử lý item_id để đảm bảo nó là một integer hoặc UUID hợp lệ
        # Chuyển đổi nếu item_id chứa "/" (như trường hợp của categories)
        str_id = str(item_id)
        if "/" in str_id and collection_name == COLLECTIONS["categories"]:
            # Sử dụng hàm convert_category_id_for_qdrant để tạo ID nhất quán
            query_id = convert_category_id_for_qdrant(str_id)
        else:
            # Nếu ID đã là số, sử dụng trực tiếp
            try:
                query_id = int(item_id)
            except (ValueError, TypeError):
                # Nếu không thể chuyển đổi thành int, sử dụng giá trị gốc
                query_id = item_id
                
        # Tìm kiếm item theo ID
        result = qdrant.retrieve(
            collection_name=collection_name,
            ids=[query_id]
        )
        # Nếu có kết quả trả về, item đã tồn tại
        return len(result) > 0
    except Exception as e:
        logger.error(f"Lỗi khi kiểm tra item ID {item_id} trong collection {collection_name}: {e}")
        return False


def convert_category_id_for_qdrant(category_id):
    """
    Chuyển đổi category_id thành ID hợp lệ cho Qdrant
    """
    str_id = str(category_id)
    if "/" in str_id:
        # Nếu id chứa ký tự "/", tạo một hash từ chuỗi để làm id
        import hashlib
        # Tạo hash từ chuỗi id ban đầu để làm id cho Qdrant
        hash_id = int(hashlib.md5(str_id.encode()).hexdigest(), 16) % (2**31)
        return hash_id
    else:
        # Nếu ID đã là số, sử dụng trực tiếp
        try:
            return int(category_id)
        except (ValueError, TypeError):
            # Nếu không thể chuyển đổi thành int, trả về None
            logger.error(f"Không thể chuyển đổi ID {category_id} thành số nguyên hoặc hash")
            return None


def run_embedding(collection_type: str = None, item_id: int = None):
    """
    Chạy quá trình tạo embedding
    
    Args:
        collection_type: Loại collection cần tạo embedding ('products', 'faqs', 'reviews', 'categories', 'chats')
                         Nếu None thì tạo embedding cho tất cả các collections
        item_id: ID của item cần tạo embedding. 
                 Nếu None thì tạo embedding cho tất cả các items trong collection
    """
    
    start_time = time.time()
    logger.info(f"Bắt đầu quá trình tạo embedding...")
    
    # Đảm bảo các collections tồn tại
    ensure_collections_exist()
    
    # Nếu chỉ định cả collection_type và item_id
    if collection_type and item_id:
        with Session() as session:
            if collection_type == "products":
                # Kiểm tra xem item đã tồn tại trong Qdrant chưa
                if check_item_exists_in_qdrant(COLLECTIONS["products"], item_id):
                    logger.info(f"Sản phẩm ID: {item_id} đã tồn tại trong Qdrant, bỏ qua")
                else:
                    logger.info(f"Tạo embedding cho sản phẩm ID: {item_id}")
                    add_product_to_qdrant(item_id)
            elif collection_type == "faqs":
                if check_item_exists_in_qdrant(COLLECTIONS["faqs"], item_id):
                    logger.info(f"FAQ ID: {item_id} đã tồn tại trong Qdrant, bỏ qua")
                else:
                    logger.info(f"Tạo embedding cho FAQ ID: {item_id}")
                    add_faq_to_qdrant(item_id)
            elif collection_type == "reviews":
                if check_item_exists_in_qdrant(COLLECTIONS["reviews"], item_id):
                    logger.info(f"Đánh giá ID: {item_id} đã tồn tại trong Qdrant, bỏ qua")
                else:
                    logger.info(f"Tạo embedding cho đánh giá ID: {item_id}")
                    add_review_to_qdrant(item_id)
            elif collection_type == "categories":
                if check_item_exists_in_qdrant(COLLECTIONS["categories"], item_id):
                    logger.info(f"Danh mục ID: {item_id} đã tồn tại trong Qdrant, bỏ qua")
                else:
                    logger.info(f"Tạo embedding cho danh mục ID: {item_id}")
                    try:
                        # Tạo một ID mới phù hợp nếu category_id chứa ký tự "/"
                        if "/" in str(item_id):
                            processed_id = convert_category_id_for_qdrant(item_id)
                            if processed_id:
                                add_category_to_qdrant(item_id)
                            else:
                                logger.error(f"Không thể tạo ID hợp lệ cho Category ID {item_id}")
                        else:
                            add_category_to_qdrant(item_id)
                    except Exception as e:
                        logger.error(f"Lỗi khi xử lý Category ID {item_id}: {e}")
            elif collection_type == "chats":
                if check_item_exists_in_qdrant(COLLECTIONS["chats"], item_id):
                    logger.info(f"Chat ID: {item_id} đã tồn tại trong Qdrant, bỏ qua")
                else:
                    logger.info(f"Tạo embedding cho chat ID: {item_id}")
                    try:
                        add_chat_to_qdrant(item_id)
                    except Exception as e:
                        logger.error(f"Lỗi khi xử lý Chat ID {item_id}: {e}")
            else:
                logger.error(f"Loại collection không hợp lệ: {collection_type}")
    
    # Nếu chỉ chỉ định collection_type
    elif collection_type:
        with Session() as session:
            if collection_type == "products":
                logger.info("Tạo embedding cho sản phẩm chưa có trong Qdrant")
                products = session.query(Product).all()
                for product in products:
                    if not check_item_exists_in_qdrant(COLLECTIONS["products"], product.product_id):
                        logger.info(f"Tạo embedding cho sản phẩm ID: {product.product_id}")
                        add_product_to_qdrant(product.product_id)
                    else:
                        logger.info(f"Sản phẩm ID: {product.product_id} đã tồn tại trong Qdrant, bỏ qua")
            elif collection_type == "faqs":
                logger.info("Tạo embedding cho FAQ chưa có trong Qdrant")
                faqs = session.query(FQA).all()
                for faq in faqs:
                    if not check_item_exists_in_qdrant(COLLECTIONS["faqs"], faq.id):
                        logger.info(f"Tạo embedding cho FAQ ID: {faq.id}")
                        add_faq_to_qdrant(faq.id)
                    else:
                        logger.info(f"FAQ ID: {faq.id} đã tồn tại trong Qdrant, bỏ qua")
            elif collection_type == "reviews":
                logger.info("Tạo embedding cho đánh giá chưa có trong Qdrant")
                reviews = session.query(Review).all()
                for review in reviews:
                    if not check_item_exists_in_qdrant(COLLECTIONS["reviews"], review.review_id):
                        logger.info(f"Tạo embedding cho đánh giá ID: {review.review_id}")
                        add_review_to_qdrant(review.review_id)
                    else:
                        logger.info(f"Đánh giá ID: {review.review_id} đã tồn tại trong Qdrant, bỏ qua")
            elif collection_type == "categories":
                logger.info("Tạo embedding cho danh mục chưa có trong Qdrant")
                categories = session.query(Category).all()
                for category in categories:
                    try:
                        category_id = category.category_id
                        if not check_item_exists_in_qdrant(COLLECTIONS["categories"], category_id):
                            logger.info(f"Tạo embedding cho danh mục ID: {category_id}")
                            add_category_to_qdrant(category_id)
                        else:
                            logger.info(f"Danh mục ID: {category_id} đã tồn tại trong Qdrant, bỏ qua")
                    except Exception as e:
                        logger.error(f"Lỗi khi xử lý danh mục: {e}")
            elif collection_type == "chats":
                logger.info("Tạo embedding cho chat chưa có trong Qdrant")
                chats = session.query(Chat).all()
                for chat in chats:
                    try:
                        chat_id = chat.id
                        if not check_item_exists_in_qdrant(COLLECTIONS["chats"], chat_id):
                            logger.info(f"Tạo embedding cho chat ID: {chat_id}")
                            add_chat_to_qdrant(chat_id)
                        else:
                            logger.info(f"Chat ID: {chat_id} đã tồn tại trong Qdrant, bỏ qua")
                    except Exception as e:
                        logger.error(f"Lỗi khi xử lý chat: {e}")
            else:
                logger.error(f"Loại collection không hợp lệ: {collection_type}")
    
    # Nếu không chỉ định cả hai, tạo embedding cho tất cả các items chưa có trong Qdrant
    else:
        logger.info("Tạo embedding cho dữ liệu chưa có trong Qdrant")
        # Thực hiện quy trình kiểm tra + thêm cho từng collection
        with Session() as session:
            # Products
            logger.info("Kiểm tra và tạo embedding cho sản phẩm chưa có trong Qdrant")
            products = session.query(Product).all()
            for product in products:
                if not check_item_exists_in_qdrant(COLLECTIONS["products"], product.product_id):
                    add_product_to_qdrant(product.product_id)
            
            # FAQs
            logger.info("Kiểm tra và tạo embedding cho FAQ chưa có trong Qdrant")
            faqs = session.query(FQA).all()
            for faq in faqs:
                if not check_item_exists_in_qdrant(COLLECTIONS["faqs"], faq.id):
                    add_faq_to_qdrant(faq.id)
            
            # Reviews
            logger.info("Kiểm tra và tạo embedding cho đánh giá chưa có trong Qdrant")
            reviews = session.query(Review).all()
            for review in reviews:
                if not check_item_exists_in_qdrant(COLLECTIONS["reviews"], review.review_id):
                    add_review_to_qdrant(review.review_id)
            
            # Categories
            logger.info("Kiểm tra và tạo embedding cho danh mục chưa có trong Qdrant")
            categories = session.query(Category).all()
            for category in categories:
                try:
                    category_id = category.category_id
                    if not check_item_exists_in_qdrant(COLLECTIONS["categories"], category_id):
                        add_category_to_qdrant(category_id)
                except Exception as e:
                    logger.error(f"Lỗi khi xử lý danh mục: {e}")
            
            # Chats
            logger.info("Kiểm tra và tạo embedding cho chat chưa có trong Qdrant")
            chats = session.query(Chat).all()
            for chat in chats:
                try:
                    chat_id = chat.id
                    if not check_item_exists_in_qdrant(COLLECTIONS["chats"], chat_id):
                        add_chat_to_qdrant(chat_id)
                except Exception as e:
                    logger.error(f"Lỗi khi xử lý chat: {e}")
    
    elapsed_time = time.time() - start_time
    logger.info(f"Hoàn thành quá trình tạo embedding trong {elapsed_time:.2f} giây")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tạo embedding cho dữ liệu E-commerce")
    parser.add_argument("--type", help="Loại collection cần tạo embedding (products, faqs, reviews, categories, chats)")
    parser.add_argument("--id", type=int, help="ID của item cần tạo embedding")
    
    args = parser.parse_args()
    run_embedding(args.type, args.id) 