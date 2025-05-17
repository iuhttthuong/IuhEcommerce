import sys
import uuid
from concurrent.futures import ThreadPoolExecutor
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from env import env
from embedding.generate_embeddings import generate_embedding
from embedding.process import preprocess_product
from db import Session
from models.products import Product
from repositories.products import ProductRepositories

QD_COLLECTION = "product_name_embeddings"

# Kết nối Qdrant
qdrant = QdrantClient(f"http://localhost:{env.QD_PORT}")

def ensure_collection_exists():
    collections = qdrant.get_collections().collections
    collection_names = [col.name for col in collections]

    if QD_COLLECTION not in collection_names:
        qdrant.create_collection(
            collection_name=QD_COLLECTION,
            vectors_config={"default": VectorParams(size=3072, distance=Distance.COSINE)},
            on_disk_payload=False  # Ensure vectors are stored
        )

        print(f"✅ Đã tạo collection '{QD_COLLECTION}'.")
    else:
        print(f"ℹ️ Collection '{QD_COLLECTION}' đã tồn tại.")

def add_product_to_qdrant(product_id: str):
    try:
        product_info = ProductRepositories.get_info(product_id)
        product_data = preprocess_product(product_info)
        embedding = generate_embedding(product_data)
        product = product_info.get("product", {})
        if embedding:
            point = PointStruct(
                id=product_id,
                vector={"default": embedding},
                payload={
                    "product_id": product_id,
                    "name": product.name,
                    "description": product.description,
                }
            )
            qdrant.upsert(collection_name=QD_COLLECTION, points=[point])
            print(f"✅ Đã thêm embedding cho sản phẩm ID {product_id}.")
        else:
            print(f"❌ Không thể tạo embedding cho sản phẩm ID {product_id}.")

    except Exception as e:
        print(f"⚠️ Lỗi khi xử lý sản phẩm ID {product_id}: {e}")

def process_all_products():
    with Session() as session:
        products = session.query(Product).all()

        # Use ThreadPoolExecutor for concurrent processing of products
        with ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(lambda product: add_product_to_qdrant(product.product_id), products)
    
    print("🎉 Đã hoàn tất việc thêm embeddings vào Qdrant.")

def main():
    ensure_collection_exists()
    process_all_products()

if __name__ == "__main__":
    main()
