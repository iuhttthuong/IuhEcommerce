import sys
from psycopg2.extras import execute_values
import json
import psycopg2
from datetime import datetime
from env import env

from import_data.tools import *

from models.sellers import SellerCreate, Seller
from models.brands import BrandCreate, Brand 
from models.categories import CategoryCreate, Category
from models.products import Product, ProductCreate
from models.warranties import Warranty, WarrantyCreate
from models.product_images import ProductImage, ProductImageCreate


error_log = []

# Connection details
db_params = {
    "dbname": env.DB_NAME,
    "user": env.DB_USER,
    "password": env.DB_PASSWORD,
    "host": env.DB_HOST,  
    "port": env.DB_PORT,  
}

try:
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print(f"Connected to: {db_version}")

    # Read the JSON files
    try:
        with open("data/crawl_data_info_proper.json", "r", encoding="utf-8") as f:
            data_crawl = json.load(f)
    except Exception as e:
        error_log.append(f"Error reading crawl data: {e}")
        data_crawl = []

    try:
        with open("data/product_data_info_proper.json", "r", encoding="utf-8") as f:
            data_product = json.load(f)
    except Exception as e:
        error_log.append(f"Error reading product data: {e}")
        data_product = []

    try:
        with open("data/product_data_test_merge.json", "r", encoding="utf-8") as f:
            data_brand = json.load(f)

    except Exception as e:
        error_log.append(f"Error reading brand data: {e}")
        data_brand = []

        
## table seller

    def check_seller(seller_id):
        if not seller_id:
            return False
        cursor.execute("SELECT seller_id FROM sellers WHERE seller_id = %s", (seller_id,))
        return cursor.fetchone() is not None

    def add_seller(i):
        try:
            cursor.execute(
                """
                INSERT INTO sellers (seller_id, seller_name, seller_type, seller_link, seller_logo_url, seller_store_id,
                                    seller_is_best_store, is_seller, is_seller_in_chat_whitelist,
                                    is_offline_installment_supported, store_rating, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    data_crawl[i].get("seller_id"),
                    data_product[i].get("current_seller").get("name"),
                    None,
                    data_product[i].get("current_seller").get("link"),
                    data_product[i].get("current_seller").get("logo"),
                    data_product[i].get("current_seller").get("store_id"),
                    None,
                    None,
                    data_product[i].get("is_seller_in_chat_whitelist"),
                    data_product[i] .get("current_seller").get("is_offline_installment_supported"),
                    None,
                    datetime.now(),
                    datetime.now()
                )   
            )
            conn.commit()
        except Exception as e:
            error_log.append(f"Error adding seller {data_crawl[i].get('seller_id')}: {e}")
            conn.rollback()

    def add_sellers():
        if not data_crawl or data_product:
            print("khong co du lieu")
            
        for i in range(1000):
            
            seller_id = data_crawl[i].get("seller_id")
            if seller_id and not check_seller(seller_id):
                add_seller(i)
            else:
                print(f"Seller {seller_id} already exists or is invalid.")

### table brand
    def check_brand(brand_id):
        if not brand_id:
            return False
        cursor.execute("SELECT brand_id FROM brands WHERE brand_id = %s", (brand_id,))
        return cursor.fetchone() is not None

    def add_brand(i):
        try:
            cursor.execute(
                """
                INSERT INTO brands (brand_id, brand_name, brand_slug, brand_country, is_top_brand)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    data_brand[i]['brand']["id"],
                    data_brand[i]['brand']["name"],
                    data_brand[i]['brand']["slug"],
                    get_attribute_value(data_brand[i]["specifications"], "brand_country"),
                    data_product[i]['tracking_info']['amplitude']['is_top_brand'],
                )   
            )
            conn.commit()
        except Exception as e:
            error_log.append(f"Error adding brand {data_brand[i].get('brand_id')}: {e}")
            conn.rollback()

    def add_brands():
        if not data_brand:
            print("khong co du lieu")
            
        for i in range(1000):
            
            brand_id = data_brand[i]['brand']["id"]
            if brand_id and not check_brand(brand_id):
                add_brand(i)
            else:
                print(f"Brand {brand_id} already exists or is invalid.")

## table categories
    def check_category(category_id):
        if not category_id:
            return False
        cursor.execute("SELECT category_id FROM categories WHERE category_id = %s", (category_id,))
        return cursor.fetchone() is not None

    def add_category(data):
        try:
            category = CategoryCreate(**data)
            cursor.execute(
                """
                INSERT INTO categories (category_id, name, parent_id, level, path)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    category.category_id if category.category_id not in (0, None) else 1,
                    category.name,
                    category.parent_id,
                    category.level,
                    category.path
                )
            )
            conn.commit()
        except Exception as e:
            error_log.append(f"Error adding category {data.get('category_id')}: {e}")
            conn.rollback()

    def add_categories():
        if not data_product:
            print("khong co du lieu")
            
        for i in range(1000):
            
            cate_list = extract_category_info(data_product[i]['breadcrumbs']) 
            for data in cate_list:
                category_id = data['category_id']
                if category_id and not check_category(category_id):
                    add_category(data)
                else:
                    print(f"Category {category_id} already exists or is invalid.")

### table product
    def check_product(product_id):
        if not product_id:
            return False
        cursor.execute("SELECT product_id FROM products WHERE product_id = %s", (product_id,))
        return cursor.fetchone() is not None      

    def add_product(i):
        try:
            quantity_value = data_product[i].get("quantity_sold", {})
            if isinstance(quantity_value, dict):
                quantity_sold = quantity_value.get("value", 0)
            else:
                quantity_sold = 0


            cursor.execute(
                """
                INSERT INTO products (product_id, name, product_short_url, description, short_description,
                                    price, original_price, discount, discount_rate, sku, review_text,
                                    quantity_sold, rating_average, review_count, order_count,
                                    favourite_count, thumbnail_url, category_id, brand_id,
                                    seller_id, shippable, availability, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s, %s)
                """,
                (
                    data_product[i]["id"],
                    data_product[i]["name"],
                    data_product[i]["short_url"],
                    data_product[i]["description"],
                    data_product[i]["short_description"],
                    data_product[i]["price"],
                    data_product[i]["original_price"],
                    data_product[i]["discount"],
                    data_product[i]["discount_rate"],
                    data_product[i]["sku"],
                    data_product[i]["review_text"],
                    quantity_sold,
                    data_product[i]["rating_average"],
                    data_product[i]["review_count"],
                    0,
                    data_product[i]["favourite_count"],
                    data_product[i]["thumbnail_url"],
                    get_last_category_id(extract_category_info(data_product[i]['breadcrumbs'])),
                    data_brand[i]['brand']["id"],
                    data_crawl[i].get("seller_id"),
                    data_crawl[i]['shippable'],
                    data_crawl[i]['availability'],
                    datetime.now(),
                    datetime.now()
                )
            )
            conn.commit()
        except Exception as e:
            error_log.append(f"Error adding product {data_product[i].get('product_id')}: {e}")
            conn.rollback()

    def add_products():
        if not data_product:
            print("khong co du lieu")
            
        for i in range(1000):
            
            product_id = data_product[i]["id"]
            if product_id and not check_product(product_id):
                add_product(i)
                print(f"Product {product_id} added successfully.")
            else:
                print(f"Product {product_id} already exists or is invalid.")
### table warriantie
    def check_warrranty(warranty_id):
        if not warranty_id:
            return False
        cursor.execute("SELECT product_id FROM warranties WHERE product_id = %s", (warranty_id,))
        return cursor.fetchone() is not None

    def add_warranty(i):    
        try:
            cursor.execute(
                """
                INSERT INTO warranties (product_id, warranty_location, warranty_period, warranty_form,
                                        warranty_url, return_policy)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    data_product[i]["id"],
                    get_value_by_name(data_brand[i]["warranty_info"], "Nơi bảo hành"),    
                    get_value_by_name(data_brand[i]["warranty_info"], "Thời gian bảo hành"),
                    get_value_by_name(data_brand[i]["warranty_info"], "Hình thức bảo hành"),
                    extract_url(data_brand[i]["warranty_info"]),
                    (lambda d: sum([b.get('content', []) for b in d.get('body', [])], []))(data_brand[i]["return_policy"])
                )
            )
            conn.commit()
        except Exception as e:
            error_log.append(f"Error adding warranty {data_product[i].get('product_id')}: {e}")
            conn.rollback()

    def add_warranties():  
        if not data_product:
            print("khong co du lieu")
            
        for i in range(1000):
            
            warranty_id = data_product[i]["id"]
            if warranty_id and not check_warrranty(warranty_id):
                add_warranty(i)
                print(f"Warranty {warranty_id} added successfully.")
            else:
                print(f"Warranty {warranty_id} already exists or is invalid.")

### table product_images
    def check_product_image(product_id):
        if not product_id:
            return False
        cursor.execute("SELECT product_id FROM product_images WHERE product_id = %s", (product_id,))
        return cursor.fetchone() is not None
    def add_product_image(i):
        try:
            product = data_product[i]
            product_id = product.get("id")
            product_images = product.get("images", [])

            for pi in product_images:
                cursor.execute(
                    """
                    INSERT INTO product_images (product_id, base_url, large_url, medium_url,
                                                small_url, thumbnail_url, position, is_gallery)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        product_id,
                        pi["base_url"],
                        pi["large_url"],
                        pi["medium_url"],
                        pi["small_url"],
                        pi["thumbnail_url"],
                        pi["position"],
                        pi["is_gallery"]
                    )   
                )
            conn.commit()

        except Exception as e:
            error_log.append(f"Error adding product image for product {id}: {e}")
            conn.rollback()

    def add_product_images():
        if not data_product:
            print("khong co du lieu")
            
        for i in range(1000):
            
            product_id = data_product[i]["id"]
            if product_id and not check_product_image(product_id):
                add_product_image(i)
                print(f"Product image {product_id} added successfully.")
            else:
                print(f"Product image {product_id} already exists or is invalid.")  

## inventory 
    def check_inventory(product_id):
        if not product_id:
            return False
        cursor.execute("SELECT product_id FROM inventories WHERE product_id = %s", (product_id,))
        return cursor.fetchone() is not None

    def add_inventory(i):
        try:
            cursor.execute(
                """
                INSERT INTO inventories (product_id, product_virtual_type, fulfillment_type)
                VALUES (%s, %s, %s)
                """,
                (
                    data_product[i]["id"],
                    data_product[i]["inventory"]["product_virtual_type"],
                    data_product[i]["inventory"]["fulfillment_type"]
                )
            )
            conn.commit()
        except Exception as e:
            error_log.append(f"Error adding inventory {data_product[i].get('product_id')}: {e}")
            conn.rollback()

    def add_inventories():
        if not data_product:
            print("khong co du lieu")
            
        for i in range(1000):
            
            product_id = data_product[i]["id"]
            if product_id and not check_inventory(product_id):
                add_inventory(i)
                print(f"Inventory {product_id} added successfully.")
            else:
                print(f"Inventory {product_id} already exists or is invalid.")
            




    # Process the data




    
    add_sellers()
    add_brands()
    add_categories()
    add_products() 
    add_warranties()
    add_product_images()
    add_inventories()

except Exception as e:
    error_log.append(f"Database connection error: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()

# Print error log if any
if error_log:
    print("Errors occurred during the process:")
    for error in error_log:
        print(error)
else:
    print("All data added successfully.")
    print("No errors occurred.")
