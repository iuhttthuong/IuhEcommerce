import json
import os
import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
from pathlib import Path
from minio import Minio
from minio.error import S3Error
import io

# MinIO configuration
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
MINIO_BUCKET = "product-images"

def get_minio_client():
    """Initialize and return MinIO client"""
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

def get_useragent():
    """
    Generates a random user agent string mimicking the format of various software versions.
    """
    lynx_version = f"Lynx/{random.randint(2, 3)}.{random.randint(8, 9)}.{random.randint(0, 2)}"
    libwww_version = f"libwww-FM/{random.randint(2, 3)}.{random.randint(13, 15)}"
    ssl_mm_version = f"SSL-MM/{random.randint(1, 2)}.{random.randint(3, 5)}"
    openssl_version = f"OpenSSL/{random.randint(1, 3)}.{random.randint(0, 4)}.{random.randint(0, 9)}"
    return f"{lynx_version} {libwww_version} {ssl_mm_version} {openssl_version}"

def download_image(url):
    """Download image from URL and return content"""
    try:
        headers = {"user-agent": get_useragent()}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        return None

def download_image_with_retry(url, max_retries=3, delay=1):
    """Download image from URL and retry up to max_retries times"""
    attempt = 0
    while attempt < max_retries:
        image_data = download_image(url)
        if image_data:
            return image_data
        attempt += 1
        if attempt < max_retries:
            print(f"Retrying download for {url} (attempt {attempt}/{max_retries})...")
            time.sleep(delay)
    print(f"Failed to download {url} after {max_retries} attempts.")
    return None

def upload_to_minio(minio_client, product_id, image_data, file_name):
    """Upload image to MinIO"""
    try:
        object_name = f"{product_id}/{file_name}"
        minio_client.put_object(
            MINIO_BUCKET,
            object_name,
            io.BytesIO(image_data),
            len(image_data),
            content_type="image/jpeg"
        )
        return f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET}/{object_name}"
    except S3Error as e:
        print(f"Error uploading to MinIO: {e}")
        return None

def process_product(product, minio_client):
    """Process a product and upload all its images to MinIO, then update product['images'] with minio urls"""
    product_id = product.get('id')
    if not product_id:
        return None
    images = product.get('images', [])
    if not images:
        return product
    minio_urls = []
    for idx, image in enumerate(images):        
        image_url = image.get('large_url') or image.get('medium_url') or image.get('base_url')
        if not image_url or image_url == "https://salt.tikicdn.com/cache/w1200/media/catalog/product/f5/15/2228f38cf84d1b8451bb49e2c4537081.png":
            minio_urls.append(None)
            continue
        parsed_url = urlparse(image_url)
        file_name = os.path.basename(parsed_url.path)
        if not file_name:
            file_name = f"image_{idx}.jpg"
        object_name = f"{product_id}/{file_name}"
        # Check if object already exists in MinIO
        try:
            minio_client.stat_object(MINIO_BUCKET, object_name)
            # If exists, just use the URL
            minio_url = f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET}/{object_name}"
            minio_urls.append(minio_url)
            # print(f"Image already exists in MinIO: {minio_url}")
            continue
        except S3Error:
            pass  # Not found, proceed to download and upload
        # Retry download until success
        image_data = download_image_with_retry(image_url)
        minio_url = None
        if image_data:
            minio_url = upload_to_minio(minio_client, product_id, image_data, file_name)
        minio_urls.append(minio_url)
        time.sleep(random.uniform(0.5, 1.5))
    # Gán lại danh sách minio url vào product['images']
    product['images'] = minio_urls
    return product

def main():
    # Initialize MinIO client
    minio_client = get_minio_client()
    
    # Ensure bucket exists
    try:
        if not minio_client.bucket_exists(MINIO_BUCKET):
            minio_client.make_bucket(MINIO_BUCKET)
            print(f"Created bucket: {MINIO_BUCKET}")
    except S3Error as e:
        print(f"Error with MinIO bucket: {e}")
        return

    # Read JSON file
    try:
        with open('product_data_merge.json', 'r', encoding='utf-8') as f:
            products = [json.loads(line) for line in f.readlines()]
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return
    
    # Use ThreadPoolExecutor for parallel processing
    processed_products = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_product, product, minio_client) for product in products]
        
        # Wait for all tasks to complete
        for future in as_completed(futures):
            try:
                processed_product = future.result()
                if processed_product:
                    processed_products.append(processed_product)
            except Exception as e:
                print(f"Error processing product: {e}")
    
    # Save processed products with minio image urls to a new file
    with open('product_data_with_minio.json', 'w', encoding='utf-8') as f:
        for prod in processed_products:
            f.write(json.dumps(prod, ensure_ascii=False) + '\n')
    print(f"Đã lưu dữ liệu sản phẩm với path ảnh MinIO vào product_data_with_minio.json")

if __name__ == "__main__":
    main()