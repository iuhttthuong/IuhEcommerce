from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import requests
import time
import random
import re

def get_useragent():
    """
    Generates a random user agent string mimicking the format of various software versions.

    The user agent string is composed of:
    - Lynx version: Lynx/x.y.z where x is 2-3, y is 8-9, and z is 0-2
    - libwww version: libwww-FM/x.y where x is 2-3 and y is 13-15
    - SSL-MM version: SSL-MM/x.y where x is 1-2 and y is 3-5
    - OpenSSL version: OpenSSL/x.y.z where x is 1-3, y is 0-4, and z is 0-9

    Returns:
        str: A randomly generated user agent string.
    """
    lynx_version = f"Lynx/{random.randint(2, 3)}.{random.randint(8, 9)}.{random.randint(0, 2)}"
    libwww_version = f"libwww-FM/{random.randint(2, 3)}.{random.randint(13, 15)}"
    ssl_mm_version = f"SSL-MM/{random.randint(1, 2)}.{random.randint(3, 5)}"
    openssl_version = f"OpenSSL/{random.randint(1, 3)}.{random.randint(0, 4)}.{random.randint(0, 9)}"
    return f"{lynx_version} {libwww_version} {ssl_mm_version} {openssl_version}"

# Tạo danh sách các user agent khác nhau
# user_agents = []

# Thêm các user agent được tạo ngẫu nhiên vào danh sách
# for _ in range(100):
#     user_agents.append(get_useragent())

output_file = "product_data_info.json"
input_file = 'crawl_data_info.json'

with open(input_file, 'r', encoding='utf-8') as f:
    data = [json.loads(line) for line in f.readlines()]

for item in data:
    item["detail_product_url"] = f"https://tiki.vn/api/v2/products/{item['id']}?platform=web&spid={item['seller_product_id']}"

session = requests.Session()

list_product_detail_collections = {
    'id', 'master_id', 'sku', 'name', 'url_key', 'short_url', 'short_description', 'price', 'list_price',
    'original_price', 'tracking_info', 'discount', 'discount_rate', 'rating_average', 'review_count', 'review_text',
    'favourite_count', 'thumbnail_url', 'has_ebook', 'inventory_status', 'inventory_type', 'productset_group_name',
    'is_fresh', 'seller', 'is_flower', 'has_buynow', 'is_gift_card', 'salable_type', 'data_version', 'day_ago_created',
    'all_time_quantity_sold', 'meta_title', 'meta_description', 'meta_keywords', 'is_baby_milk', 'is_acoholic_drink',
    'description', 'images', 'warranty_policy', 'brand', 'current_seller', 'other_sellers', 'specifications',
    'product_links', 'gift_item_title', 'configurable_options', 'configurable_products', 'services_and_promotions',
    'promitions', 'stock_item', 'quantity_sold', 'categories', 'breadcrumbs', 'installment_info_v2', 'video_url',
    'is_seller_in_chat_whitelist', 'inventory', 'warranty_info', 'return_and_exchange_policy',
    'is_tier_pricing_available', 'is_tier_pricing_eligible', 'benefits', 'return_policy', 
}

def save_to_file(data_batch):
    """ Lưu nhiều dòng vào file để giảm số lần ghi đĩa """
    if not data_batch:
        return
        
    # Đọc dữ liệu hiện có từ file một lần duy nhất
    existing_products = set()
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            # Đọc toàn bộ file vào bộ nhớ
            content = f.read()
            # Tìm tất cả các ID sản phẩm bằng regex
            product_ids = re.findall(r'"id":\s*(\d+)', content)
            existing_products = set(product_ids)
    except FileNotFoundError:
        pass  # File chưa tồn tại, bỏ qua

    # Lọc ra các sản phẩm chưa tồn tại
    new_products = []
    for data in data_batch:
        if 'id' in data and str(data['id']) not in existing_products:
            new_products.append(data)
            # Thêm ID vào set để tránh trùng lặp trong cùng một batch
            existing_products.add(str(data['id']))

    # Ghi các sản phẩm mới vào file
    if new_products:
        with open(output_file, "a", encoding="utf-8") as f:
            f.writelines(json.dumps(data, ensure_ascii=False) + "\n" for data in new_products)
        print(f"Đã lưu {len(new_products)} sản phẩm mới vào file")
    else:
        print("Không có sản phẩm mới để lưu")

def filter_data(item):
    """ Lọc dữ liệu chỉ lấy các trường quan trọng """
    return {key: item[key] for key in list_product_detail_collections if key in item}

def fetch_product_data(item):
    """ Gửi request đến API để lấy dữ liệu chi tiết của sản phẩm với retry liên tục cho đến khi thành công """
    url = item['detail_product_url']
    while True:
        try:
            # Chọn ngẫu nhiên một user agent từ danh sách
            headers = {"user-agent": get_useragent()}
            response = session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 429:
                wait_time = random.uniform(5, 10)
                print(f"⚠️  429 Too Many Requests. Đợi {wait_time:.2f} giây rồi thử lại...")
                time.sleep(wait_time)
                continue
                
            response.raise_for_status()
            return filter_data(response.json())
            # return response.json()
            
        except requests.RequestException as e:
            print(f"Lỗi khi lấy dữ liệu từ {url}: {e}")
            wait_time = random.uniform(1, 3)
            # print(f"Đợi {wait_time:.2f} giây rồi thử lại...")
            time.sleep(wait_time)

batch_size = 20  
num_threads = 5 

with ThreadPoolExecutor(max_workers=num_threads) as executor:
    futures = {executor.submit(fetch_product_data, item): item for item in data}
    data_batch = []

    for future in as_completed(futures):
        result = future.result()
        if result:
            data_batch.append(result)
        
        # Khi batch đầy, ghi dữ liệu vào file
        if len(data_batch) >= batch_size:
            save_to_file(data_batch)
            data_batch.clear()

if data_batch:
    save_to_file(data_batch)
