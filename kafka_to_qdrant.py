import json
import time
from kafka import KafkaConsumer
from embedding.process import (
    preprocess_product, preprocess_faq, preprocess_review,
    preprocess_category, preprocess_chat, preprocess_search_log
)
from embedding.main import embed_and_upsert_to_qdrant

# Map các topic Kafka với hàm tiền xử lý tương ứng
TOPIC_MAP = {
    'dbserver1.public.products': preprocess_product,
    'dbserver1.public.fqas': preprocess_faq,
    'dbserver1.public.reviews': preprocess_review,
    'dbserver1.public.categories': preprocess_category,
    'dbserver1.public.chat': preprocess_chat,
    # 'dbserver1.public.search_log': preprocess_search_log,
}

print('Khởi tạo Kafka consumer...')
consumer = KafkaConsumer(
    *TOPIC_MAP.keys(),
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='embedding-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print('Bắt đầu lắng nghe các thay đổi từ PostgreSQL...')
for message in consumer:
    event = message.value
    topic = message.topic
    preprocess_func = TOPIC_MAP.get(topic)
    
    if not preprocess_func:
        print(f"⚠️ Không tìm thấy hàm xử lý cho topic {topic}")
        continue
        
    payload = event.get('payload', {})
    after = payload.get('after')
    
    if after:
        try:
            # Tiền xử lý dữ liệu
            text = preprocess_func(after)
            print(f"✅ Đã xử lý dữ liệu từ {topic}: {text[:100]}...")
            
            # Tạo embedding và lưu vào Qdrant
            embed_and_upsert_to_qdrant(after, text, topic)
        except Exception as e:
            print(f"❌ Lỗi khi xử lý message từ {topic}: {e}")
    else:
        print(f"ℹ️ Không có dữ liệu mới trong event từ {topic}")
    
    time.sleep(0.1)  # Tránh quá tải
