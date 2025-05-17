import json
import os
import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
from pathlib import Path

def get_useragent():
    """
    Generates a random user agent string mimicking the format of various software versions.
    """
    lynx_version = f"Lynx/{random.randint(2, 3)}.{random.randint(8, 9)}.{random.randint(0, 2)}"
    libwww_version = f"libwww-FM/{random.randint(2, 3)}.{random.randint(13, 15)}"
    ssl_mm_version = f"SSL-MM/{random.randint(1, 2)}.{random.randint(3, 5)}"
    openssl_version = f"OpenSSL/{random.randint(1, 3)}.{random.randint(0, 4)}.{random.randint(0, 9)}"
    return f"{lynx_version} {libwww_version} {ssl_mm_version} {openssl_version}"

def create_image_directory(product_id):
    """Tạo thư mục để lưu hình ảnh của sản phẩm"""
    directory = f"images/{product_id}"
    os.makedirs(directory, exist_ok=True)
    return directory

def download_image(url, save_path):
    """Tải hình ảnh từ URL và lưu vào đường dẫn được chỉ định"""
    try:
        headers = {"user-agent": get_useragent()}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Lỗi khi tải hình ảnh từ {url}: {e}")
        return False

def process_product(product):
    """Xử lý một sản phẩm và tải tất cả hình ảnh của nó"""
    product_id = product.get('id')
    if not product_id:
        return
    
    # Tạo thư mục cho sản phẩm
    directory = create_image_directory(product_id)
    
    # Kiểm tra xem thư mục đã có hình ảnh chưa
    existing_images = set()
    if os.path.exists(directory):
        existing_images = {f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))}
    
    # Lấy danh sách hình ảnh
    images = product.get('images', [])
    if not images:
        return
    
    # Tải từng hình ảnh
    for idx, image in enumerate(images):
        # Sử dụng URL lớn nhất có sẵn
        image_url = image.get('large_url') or image.get('medium_url') or image.get('base_url')
        if not image_url:
            continue
            
        # Tạo tên file từ URL
        parsed_url = urlparse(image_url)
        file_name = os.path.basename(parsed_url.path)
        if not file_name:
            file_name = f"image_{idx}.jpg"
            
        # Kiểm tra xem file đã tồn tại chưa
        if file_name in existing_images:
            print(f"Bỏ qua hình ảnh đã tồn tại: {file_name}")
            continue
            
        save_path = os.path.join(directory, file_name)
        
        # Tải hình ảnh
        if download_image(image_url, save_path):
            print(f"Đã tải thành công: {save_path}")
            existing_images.add(file_name)  # Thêm vào danh sách đã tải
        else:
            print(f"Không thể tải: {image_url}")
            
        # Đợi một chút giữa các request
        time.sleep(random.uniform(0.5, 1.5))

def main():
    # Đọc file JSON
    try:
        with open('product_data_info.json', 'r', encoding='utf-8') as f:
            products = [json.loads(line) for line in f.readlines()]
    except Exception as e:
        print(f"Lỗi khi đọc file JSON: {e}")
        return
    
    # Tạo thư mục gốc cho hình ảnh
    os.makedirs("images", exist_ok=True)
    
    # Sử dụng ThreadPoolExecutor để tải hình ảnh song song
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_product, product) for product in products]
        
        # Đợi tất cả các task hoàn thành
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Lỗi khi xử lý sản phẩm: {e}")

if __name__ == "__main__":
    main() 