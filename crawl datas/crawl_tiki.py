from concurrent.futures import ThreadPoolExecutor
import json
import requests
import re

cate_re = ['11312', '15078', '1520', '1686', '1703', '17166', '1789', '1801', '1815', '1846', '1882', '1883', '1975', '2549', '27498', '27616', '4221', '4384', '44792', '6000', '8322', '8371', '8594', '915', '931', '976']

output_file = "crawl_data_info.json"
headers = {"user-agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'}

session = requests.Session()  # Dùng Session để giảm overhead

def save_to_file(data_batch):
    """ Ghi nhiều dòng vào file cùng lúc để giảm số lần I/O """
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

def fetch_data(category, price):
    """ Gửi request đến API và trả về dữ liệu JSON """
    url = f"https://tiki.vn/api/personalish/v1/blocks/listings?version=home-persionalized&trackity_id=1016758d-050b-b91b-503a-ccc8de815bed&category={category}&price={price},{price+99999}&page={page}"
    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json().get('data', [])
    except requests.RequestException as e:
        return []

def filter_data(item):
    """ Lọc dữ liệu theo danh sách khóa quan trọng """
    list_data_product_collections = {'id', 'sku', 'name', 'url_key', 'url_path', 'price', 'discount', 'discount_rate', 'rating_average', 'review_count', 'order_count', 'favourite_count', 'thumbnail_url', 'thumbnail_width', 'thumbnail_height', 'productset_id', 'seller_product_id', 'quantity_sold', 'original_price', 'shippable', 'advertisement', 'availability', 'primary_category_path', 'product_reco_score', 'seller_id', 'visible_impression_info'}
    return {key: item[key] for key in list_data_product_collections if key in item}

def fetch_page(category, price, page):
    """ Gửi request song song """
    url = f"https://tiki.vn/api/personalish/v1/blocks/listings?version=home-persionalized&trackity_id=1016758d-050b-b91b-503a-ccc8de815bed&category={category}&price={price},{price+99999}&page={page}"
    try:
        response = session.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        return response.json().get('data', [])
    except requests.RequestException as e:
        # print(f"Lỗi khi lấy dữ liệu từ {url}: {e}")
        return []

for category in cate_re:
    price = 1
    while True:
        has_data = False
        data_batch = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(lambda p: fetch_page(category, price, p), range(51)))

        for data in results:
            if data:
                has_data = True
                data_batch.extend(filter_data(item) for item in data)

        save_to_file(data_batch)

        price += 10000
        if price > 30000: break
        if not has_data:
            print(f"Dừng vì không còn dữ liệu {category} ở price range {price-100000}-{price-1}")
            break
