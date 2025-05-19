import os
import shutil
import requests

# Đường dẫn tới thư mục chứa collection
collection_path = "/qdrant/storage/collections/database_embeddings/0/"
qdrant_url = "http://localhost:6333"  # Cổng Qdrant API

# Kiểm tra sự tồn tại của collection
if os.path.exists(collection_path):
    print(f"Collection found at {collection_path}. Proceeding with import.")

    # Tạo dữ liệu cấu hình collection, nếu cần (thường là JSON)
    config_file = os.path.join(collection_path, "config.json")
    if os.path.exists(config_file):
        print(f"Configuration file {config_file} found. Proceeding with import.")
        
        # Giả sử collection đã được định dạng đúng, tiến hành gửi yêu cầu import
        with open(config_file, 'rb') as f:
            response = requests.post(f"{qdrant_url}/collections", files={"file": f})
            if response.status_code == 200:
                print("Collection imported successfully.")
            else:
                print(f"Failed to import collection. Status code: {response.status_code}")
    else:
        print(f"Config file missing in {collection_path}. Cannot import collection.")
else:
    print(f"Collection directory not found: {collection_path}")
