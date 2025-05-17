import sys
import uuid
from concurrent.futures import ThreadPoolExecutor
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from env import env
from embedding.generate_embeddings import generate_embedding
from db import Session
from models.fqas import FQA, FQAModel
from services.fqas import FQAsService

QD_COLLECTION = "poli_embeddings"

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

def process_fqa(fqa: FQAModel):
    # Tạo vector embedding
    embedding = generate_embedding(fqa.question)
    if not embedding:
        print(f"❌ Không thể tạo embedding cho câu hỏi: {fqa.question}")
        return

    # Tạo ID ngẫu nhiên cho điểm
    point_id = fqa.id


    if embedding:
        point = PointStruct(
            id=point_id,
            vector={"default": embedding},
            payload={
                "fqa_id": point_id,
                "question": fqa.question,
                "answer": fqa.answer,
            }
        )
        qdrant.upsert(collection_name=QD_COLLECTION, points=[point])
    else:
        print(f"❌ Không thể tạo embedding cho sản phẩm ID {point_id}.")
    print(f"✅ Đã thêm điểm với ID: {point_id} vào Qdrant.")

def add_fqa_to_qdrant(id: str):
    # Lấy sản phẩm từ DB
    with Session() as session:
        fqa = session.query(FQA).filter(FQA.id == id).first()
        if not fqa:
            print(f"❌ Không tìm thấy FQA với ID: {id}")
            return

    # Xử lý và thêm vào Qdrant
    process_fqa(fqa)
    print(f"✅ Đã thêm FQA với ID: {id} vào Qdrant.")

with Session() as session:
    # Lấy tất cả các câu hỏi từ cơ sở dữ liệu
    fqas = session.query(FQA).all()
    fqa_models = [FQAModel.from_orm(fqa) for fqa in fqas]

    # Đảm bảo collection tồn tại
    ensure_collection_exists()
 # Sử dụng ThreadPoolExecutor để xử lý song song
with ThreadPoolExecutor(max_workers=10) as executor:
    for fqa in fqa_models:
        executor.submit(process_fqa, fqa)
print("✅ Đã thêm tất cả các FQA vào Qdrant.")