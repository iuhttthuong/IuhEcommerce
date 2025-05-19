from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter
from env import env

# Kết nối Qdrant
qdrant = QdrantClient(f"http://localhost:{env.QD_PORT}")

# Tên collection
QD_COLLECTION = "database_embeddings"

# Xóa tất cả điểm trong collection bằng cách dùng filter trống
qdrant.delete(
    collection_name=QD_COLLECTION,
    points_selector=Filter(must=[])  # Xóa tất cả
)
print(f"✅ Đã xóa tất cả điểm trong collection '{QD_COLLECTION}'.")

# Hoặc nếu bạn muốn xóa luôn cả collection:
qdrant.delete_collection(collection_name=QD_COLLECTION)
print(f"🗑️ Collection '{QD_COLLECTION}' đã bị xóa hoàn toàn.")
