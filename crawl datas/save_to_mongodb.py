import json
from pymongo import MongoClient

# Cấu hình MongoDB
MONGO_URI = "mongodb://root:example@localhost:27017/"
DB_NAME = "ecommerce_lakehouse"
COLLECTION_PRODUCTS = "products"
COLLECTION_IMAGES = "images"

# Kết nối MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
products_col = db[COLLECTION_PRODUCTS]
images_col = db[COLLECTION_IMAGES]

def save_products(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            product = json.loads(line)
            prod_id = product.get('id')
            if prod_id:
                images = product.get('images', [])
                minio_paths = []
                for img in images:
                    if isinstance(img, dict):
                        minio_url = img.get('minio_url') or img.get('minio_path')
                        if not minio_url:
                            minio_url = img.get('large_url') or img.get('medium_url') or img.get('base_url')
                        minio_paths.append(minio_url)
                    else:
                        # img là chuỗi (url minio)
                        minio_paths.append(img)
                product['images'] = minio_paths
                products_col.update_one({'id': prod_id}, {'$set': product}, upsert=True)
    print(f"Đã lưu dữ liệu từ {file_path} vào MongoDB với images là path MinIO.")

if __name__ == "__main__":
    # Lưu dữ liệu sản phẩm chi tiết từ file đã có path ảnh MinIO
    save_products('product_data_with_minio.json')
    # Nếu muốn lưu dữ liệu thô ban đầu:
    # save_products('crawl_data_info.json')
