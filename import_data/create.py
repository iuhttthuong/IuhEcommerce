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

def check_table_exists(cursor, table_name):
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        );
    """, (table_name,))
    return cursor.fetchone()[0]

def create_tables_if_not_exist(cursor):
    # Create brands table
    if not check_table_exists(cursor, 'brands'):
        cursor.execute("""
            CREATE TABLE brands (
                brand_id BIGINT PRIMARY KEY,
                brand_name VARCHAR(255) NOT NULL,
                brand_slug VARCHAR(255),
                brand_country VARCHAR(255)
            );
        """)
        print("Created brands table")

    # Create categories table
    if not check_table_exists(cursor, 'categories'):
        cursor.execute("""
            CREATE TABLE categories (
                category_id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255),
                parent_id VARCHAR(255),
                level INTEGER,
                path TEXT,
                FOREIGN KEY (parent_id) REFERENCES categories(category_id)
            );
        """)
        print("Created categories table")

    # Create products table
    if not check_table_exists(cursor, 'products'):
        cursor.execute("""
            CREATE TABLE products (
                product_id BIGINT PRIMARY KEY,
                name TEXT,
                product_short_url TEXT,
                description TEXT,
                short_description TEXT,
                price DECIMAL,
                original_price DECIMAL,
                discount DECIMAL,
                discount_rate DECIMAL,
                sku VARCHAR(255),
                review_text TEXT,
                quantity_sold INTEGER,
                rating_average DECIMAL,
                review_count INTEGER,
                order_count INTEGER,
                favourite_count INTEGER,
                thumbnail_url TEXT,
                category_id VARCHAR(255) REFERENCES categories(category_id),
                brand_id BIGINT REFERENCES brands(brand_id),
                seller_id BIGINT,
                shippable BOOLEAN,
                availability BOOLEAN,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            );
        """)
        print("Created products table")

    # Create warranties table
    if not check_table_exists(cursor, 'warranties'):
        cursor.execute("""
            CREATE TABLE warranties (
                product_id BIGINT PRIMARY KEY REFERENCES products(product_id),
                warranty_location TEXT,
                warranty_period TEXT,
                warranty_form TEXT,
                warranty_url TEXT,
                return_policy TEXT
            );
        """)
        print("Created warranties table")

    # Create product_images table
    if not check_table_exists(cursor, 'product_images'):
        cursor.execute("""
            CREATE TABLE product_images (
                product_id BIGINT REFERENCES products(product_id),
                base_url TEXT NOT NULL,
                large_url TEXT NOT NULL,
                medium_url TEXT NOT NULL,
                is_gallery BOOLEAN,
                PRIMARY KEY (product_id, base_url)
            );
        """)
        print("Created product_images table")

    # Create inventories table
    if not check_table_exists(cursor, 'inventories'):
        cursor.execute("""
            CREATE TABLE inventories (
                product_id BIGINT PRIMARY KEY REFERENCES products(product_id),
                product_virtual_type VARCHAR(255),
                fulfillment_type VARCHAR(255)
            );
        """)
        print("Created inventories table")

try:
    conn = psycopg2.connect(**db_params)
    conn.autocommit = False  # Disable autocommit
    cursor = conn.cursor()

    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print(f"Connected to: {db_version}")

    # Drop existing tables if they exist
    cursor.execute("""
        DROP TABLE IF EXISTS inventories CASCADE;
        DROP TABLE IF EXISTS product_images CASCADE;
        DROP TABLE IF EXISTS warranties CASCADE;
        DROP TABLE IF EXISTS products CASCADE;
        DROP TABLE IF EXISTS categories CASCADE;
        DROP TABLE IF EXISTS brands CASCADE;
    """)
    conn.commit()
    print("Dropped existing tables")

    # Create tables if they don't exist
    create_tables_if_not_exist(cursor)
    conn.commit()
    print("Tables created/verified successfully")

    # Read the JSON files
    try:
        with open("data/crawl_data_info_proper.json", "r", encoding="utf-8") as f:
            data_crawl = json.load(f)
            print(f"Loaded {len(data_crawl)} crawl records")
    except Exception as e:
        error_log.append(f"Error reading crawl data: {e}")
        data_crawl = []

    try:
        with open("data/product_data_info_proper.json", "r", encoding="utf-8") as f:
            data_product = json.load(f)
            print(f"Loaded {len(data_product)} product records")
    except Exception as e:
        error_log.append(f"Error reading product data: {e}")
        data_product = []

    try:
        # Handle multiple JSON objects in the file
        data_brand = []
        with open("data/product_data_merge.json", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:  # Skip empty lines
                    try:
                        data_brand.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        error_log.append(f"Error parsing JSON line: {e}")
                        continue
        print(f"Loaded {len(data_brand)} brand records")
    except Exception as e:
        error_log.append(f"Error reading brand data: {e}")
        data_brand = []

    # Get the minimum length of all data arrays
    min_length = min(len(data_crawl), len(data_product), len(data_brand))
    print(f"Processing {min_length} records")

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

    def check_brand(brand_id):
        if not brand_id:
            return False
        cursor.execute("SELECT brand_id FROM brands WHERE brand_id = %s", (brand_id,))
        return cursor.fetchone() is not None

    def add_brand(i):
        try:
            brand_data = (
                data_brand[i]['brand']["id"],
                data_brand[i]['brand']["name"],
                data_brand[i]['brand']["slug"],
                get_attribute_value(data_brand[i]["specifications"], "brand_country"),
            )
            print(f"Adding brand with data: {brand_data}")
            
            cursor.execute(
                """
                INSERT INTO brands (brand_id, brand_name, brand_slug, brand_country)
                VALUES (%s, %s, %s, %s)
                """,
                brand_data
            )
            conn.commit()
            print(f"Successfully committed brand {brand_data[0]}")
        except Exception as e:
            error_log.append(f"Error adding brand {data_brand[i].get('brand_id')}: {e}")
            print(f"Error details: {str(e)}")
            conn.rollback()

    def add_brands():
        if not data_brand:
            print("No brand data available")
            return
            
        print(f"\nStarting to add brands...")
        brands_added = 0
        for i in range(min_length):
            try:
                brand_id = data_brand[i]['brand']["id"]
                if brand_id and not check_brand(brand_id):
                    add_brand(i)
                    brands_added += 1
                    if brands_added % 100 == 0:  # Log progress every 100 records
                        print(f"Added {brands_added} brands so far...")
                else:
                    print(f"Brand {brand_id} already exists or is invalid.")
            except Exception as e:
                error_log.append(f"Error processing brand at index {i}: {e}")
                print(f"Error details: {str(e)}")
        print(f"Finished adding brands. Total added: {brands_added}")

    def check_category(category_id):
        if not category_id:
            return False
        cursor.execute("SELECT category_id FROM categories WHERE category_id = %s", (category_id,))
        return cursor.fetchone() is not None

    def add_category(data):
        try:
            category_data = (
                str(data['category_id']),  # Ensure category_id is string
                data['name'],
                data['path']
            )
            print(f"Adding category with data: {category_data}")
            
            cursor.execute(
                """
                INSERT INTO categories (category_id, name, path)
                VALUES (%s, %s, %s)
                """,
                category_data
            )
            conn.commit()
            print(f"Successfully committed category {category_data[0]}")
        except Exception as e:
            error_log.append(f"Error adding category {data.get('category_id')}: {e}")
            print(f"Error details: {str(e)}")
            conn.rollback()

    def add_categories():
        if not data_product:
            print("No product data available")
            return
            
        print(f"\nStarting to add categories...")
        categories_added = 0
        all_categories = []
        
        # First, collect all categories
        for i in range(min_length):
            try:
                if 'breadcrumbs' not in data_product[i]:
                    print(f"No breadcrumbs data for product at index {i}")
                    continue
                    
                cate_list = extract_category_info(data_product[i]['breadcrumbs'])
                if not cate_list:
                    print(f"No categories extracted from breadcrumbs at index {i}")
                    continue
                    
                all_categories.extend(cate_list)
            except Exception as e:
                error_log.append(f"Error processing category at index {i}: {e}")
                print(f"Error details: {str(e)}")

        # Remove duplicates while preserving order
        unique_categories = []
        seen_ids = set()
        for cat in all_categories:
            if cat['category_id'] not in seen_ids:
                seen_ids.add(cat['category_id'])
                unique_categories.append(cat)

        # Add categories
        for data in unique_categories:
            try:
                if not data or 'category_id' not in data:
                    print(f"Invalid category data")
                    continue
                    
                category_id = data['category_id']
                if category_id and not check_category(category_id):
                    add_category(data)
                    categories_added += 1
                    if categories_added % 100 == 0:  # Log progress every 100 records
                        print(f"Added {categories_added} categories so far...")
                else:
                    print(f"Category {category_id} already exists or is invalid.")
            except Exception as e:
                error_log.append(f"Error adding category {data.get('category_id')}: {e}")
                print(f"Error details: {str(e)}")
                
        print(f"Finished adding categories. Total added: {categories_added}")

    def check_product(product_id):
        if not product_id:
            return False
        cursor.execute("SELECT product_id FROM products WHERE product_id = %s", (product_id,))
        return cursor.fetchone() is not None      

    def add_product(i):
        try:
            # Get quantity_sold value safely
            quantity_value = data_product[i].get("quantity_sold", {})
            if isinstance(quantity_value, dict):
                quantity_sold = quantity_value.get("value", 0)
            else:
                quantity_sold = 0

            # Get category_id safely
            category_info = extract_category_info(data_product[i].get('breadcrumbs', []))
            category_id = get_last_category_id(category_info) if category_info else None

            # Get brand_id safely
            brand_id = data_brand[i].get('brand', {}).get('id') if i < len(data_brand) else None

            # Get seller_id safely
            seller_id = data_crawl[i].get('seller_id') if i < len(data_crawl) else None

            # Convert availability to boolean
            availability = bool(data_crawl[i].get('availability', 0)) if i < len(data_crawl) else False

            # Prepare product data
            product_data = (
                data_product[i].get("id"),
                data_product[i].get("name"),
                data_product[i].get("short_url"),
                data_product[i].get("description"),
                data_product[i].get("short_description"),
                data_product[i].get("price"),
                data_product[i].get("original_price"),
                data_product[i].get("discount"),
                data_product[i].get("discount_rate"),
                data_product[i].get("sku"),
                data_product[i].get("review_text"),
                quantity_sold,
                data_product[i].get("rating_average"),
                data_product[i].get("review_count"),
                0,  # order_count default to 0
                data_product[i].get("favourite_count"),
                data_product[i].get("thumbnail_url"),
                category_id,
                brand_id,
                seller_id,
                data_crawl[i].get('shippable', False) if i < len(data_crawl) else False,
                availability,  # Use the converted boolean value
                datetime.now(),
                datetime.now()
            )

            print(f"Adding product with data: {product_data[0:5]}...")  # Print first 5 fields for debugging

            cursor.execute(
                """
                INSERT INTO products (
                    product_id, name, product_short_url, description, short_description,
                    price, original_price, discount, discount_rate, sku, review_text,
                    quantity_sold, rating_average, review_count, order_count,
                    favourite_count, thumbnail_url, category_id, brand_id,
                    seller_id, shippable, availability, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                product_data
            )
            conn.commit()
            print(f"Successfully committed product {product_data[0]}")

        except Exception as e:
            error_log.append(f"Error adding product {data_product[i].get('id')}: {e}")
            print(f"Error details: {str(e)}")
            conn.rollback()

    def add_products():
        if not data_product:
            print("No product data available")
            return
            
        print(f"\nStarting to add products...")
        products_added = 0
        for i in range(min_length):
            try:
                product_id = data_product[i].get("id")
                if not product_id:
                    print(f"No product ID found at index {i}")
                    continue
                    
                if not check_product(product_id):
                    add_product(i)
                    products_added += 1
                    if products_added % 100 == 0:  # Log progress every 100 records
                        print(f"Added {products_added} products so far...")
                else:
                    print(f"Product {product_id} already exists.")
            except Exception as e:
                error_log.append(f"Error processing product at index {i}: {e}")
                print(f"Error details: {str(e)}")
                
        print(f"Finished adding products. Total added: {products_added}")

    def add_warranty(i):    
        try:
            product_id = data_product[i].get("id")
            if not product_id:
                print(f"No product ID found at index {i}")
                return

            warranty_info = data_brand[i].get("warranty_info", []) if i < len(data_brand) else []
            return_policy = data_brand[i].get("return_policy", {}) if i < len(data_brand) else {}

            warranty_data = (
                product_id,
                get_value_by_name(warranty_info, "Nơi bảo hành"),    
                get_value_by_name(warranty_info, "Thời gian bảo hành"),
                get_value_by_name(warranty_info, "Hình thức bảo hành"),
                extract_url(warranty_info),
                (lambda d: sum([b.get('content', []) for b in d.get('body', [])], []))(return_policy)
            )
            print(f"Adding warranty with data: {warranty_data[0:3]}...")  # Print first 3 fields for debugging
            
            cursor.execute(
                """
                INSERT INTO warranties (product_id, warranty_location, warranty_period, warranty_form,
                                    warranty_url, return_policy)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (product_id) DO NOTHING
                """,
                warranty_data
            )
            conn.commit()
            print(f"Successfully committed warranty for product {product_id}")

        except Exception as e:
            error_log.append(f"Error adding warranty for product {product_id}: {e}")
            print(f"Error details: {str(e)}")
            conn.rollback()

    def add_warranties():  
        if not data_product:
            print("No product data available")
            return
            
        print(f"\nStarting to add warranties...")
        warranties_added = 0
        for i in range(min_length):
            try:
                product_id = data_product[i].get("id")
                if not product_id:
                    print(f"No product ID found at index {i}")
                    continue
                    
                add_warranty(i)
                warranties_added += 1
                if warranties_added % 100 == 0:  # Log progress every 100 records
                    print(f"Added {warranties_added} warranties so far...")
            except Exception as e:
                error_log.append(f"Error processing warranty at index {i}: {e}")
                print(f"Error details: {str(e)}")
                
        print(f"Finished adding warranties. Total added: {warranties_added}")

    def add_product_image(i):
        try:
            product = data_product[i]
            product_id = product.get("id")
            if not product_id:
                print(f"No product ID found at index {i}")
                return

            product_images = product.get("images", [])
            if not product_images:
                print(f"No images found for product {product_id}")
                return

            for pi in product_images:
                image_data = (
                    product_id,
                    pi.get("base_url"),
                    pi.get("large_url"),
                    pi.get("medium_url"),
                    pi.get("is_gallery", False)
                )
                print(f"Adding product image with data: {image_data}")
                
                cursor.execute(
                    """
                    INSERT INTO product_images (product_id, base_url, large_url, medium_url, is_gallery)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (product_id, base_url) DO NOTHING
                    """,
                    image_data
                )
            conn.commit()
            print(f"Successfully committed images for product {product_id}")

        except Exception as e:
            error_log.append(f"Error adding product image for product {product_id}: {e}")
            print(f"Error details: {str(e)}")
            conn.rollback()
            
    def add_product_images():
        if not data_product:
            print("No product data available")
            return
            
        print(f"\nStarting to add product images...")
        images_added = 0
        for i in range(min_length):
            try:
                product_id = data_product[i].get("id")
                if not product_id:
                    print(f"No product ID found at index {i}")
                    continue
                    
                add_product_image(i)
                images_added += 1
                if images_added % 100 == 0:  # Log progress every 100 records
                    print(f"Processed {images_added} products' images so far...")
            except Exception as e:
                error_log.append(f"Error processing product images at index {i}: {e}")
                print(f"Error details: {str(e)}")
                
        print(f"Finished adding product images. Total products processed: {images_added}")

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
            print("No product data available")
            return
            
        for i in range(min_length):
            try:
                product_id = data_product[i]["id"]
                if product_id and not check_inventory(product_id):
                    add_inventory(i)
                    print(f"Inventory {product_id} added successfully.")
                else:
                    print(f"Inventory {product_id} already exists or is invalid.")
            except Exception as e:
                error_log.append(f"Error processing inventory at index {i}: {e}")

    # Process the data in the correct order
    print("\nStarting data import process...")
    
    # First add brands
    add_brands()
    
    # Then add categories
    add_categories()
    
    # Then add products
    add_products()
    
    # Finally add related data
    add_warranties()
    add_product_images()
    add_inventories()

    # Verify data was added
    print("\nVerifying data in database...")
    cursor.execute("SELECT COUNT(*) FROM brands")
    brand_count = cursor.fetchone()[0]
    print(f"Total brands in database: {brand_count}")
    
    cursor.execute("SELECT COUNT(*) FROM categories")
    category_count = cursor.fetchone()[0]
    print(f"Total categories in database: {category_count}")
    
    cursor.execute("SELECT COUNT(*) FROM products")
    product_count = cursor.fetchone()[0]
    print(f"Total products in database: {product_count}")

except Exception as e:
    error_log.append(f"Database connection error: {e}")
    print(f"Fatal error: {str(e)}")
    if 'conn' in locals():
        conn.rollback()
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
        print("\nDatabase connection closed.")

# Print error log if any
if error_log:
    print("\nErrors occurred during the process:")
    for error in error_log:
        print(error)
else:
    print("\nAll data added successfully.")
    print("No errors occurred.")
