from qdrant_client import QdrantClient
import pandas as pd
import json
from db import Session
from models.products import Product

# Kết nối Qdrant
client = QdrantClient(host="localhost", port=6333)

# Tên collection
collection_name = "database_embeddings"

# Lấy toàn bộ điểm
scroll_result = client.scroll(
    collection_name=collection_name,
    with_payload=True,
    with_vectors=True,
    limit=5000  # tăng giới hạn nếu bạn có nhiều dữ liệu
)

# Chuyển thành DataFrame
data = [{
    "id": point.id,
    "vector": point.vector.get("default") if isinstance(point.vector, dict) else point.vector,
    "payload": point.payload
} for point in scroll_result[0]]

print(f"Đã lấy {len(data)} điểm từ Qdrant.")
## lấy id từ postgresql
with Session() as session:
    # Giả sử bạn có một bảng tên là 'products' trong PostgreSQL
    # và bạn muốn lấy tất cả các ID sản phẩm
    product_ids = session.query(Product.product_id).all()
    product_ids = [product_id[0] for product_id in product_ids]



count  = 0
for item in data:
    # kiểm tra nếu id có trong postgresql thì tăng biến đếm
    if item["id"] in product_ids:
        count += 1
    print(f"đã thheem {item['id']} vào postgresql")
print(f"Đã tìm thấy {count} ID trong PostgreSQL.")

