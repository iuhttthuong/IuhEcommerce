# sample url: https://tiki.vn/api/v2/reviews?limit=20&page=1&product_id=72711795
# url: https://tiki.vn/api/v2/reviews?limit=20&page={page}&product_id={product_id}
# truy cập vào postgres lấy thông tin từ .env
# product_id lấy từ bảng products
# lưu dữ liệu vào bảng reviews với các trường như sau:
# review_id: int (id từ url)
# product_id: int (product_id từ bảng products)
# customer_id: 1
# rating: int (rating từ url)
# comment: text (content từ url)
# review_date: timestamp without time zone (thank_count từ url)
# likes: int (thank_count từ url)
# dislikes: 0
# sample nội dung từ url: {"stars":{"1":{"count":6,"percent":4},"2":{"count":1,"percent":1},"3":{"count":7,"percent":5},"4":{"count":16,"percent":14},"5":{"count":92,"percent":76}},"rating_average":4.5,"reviews_count":122,"review_photo":{"total":23,"total_photo":27},"data":[{"id":19056639,"title":"R\u1ea5t kh\u00f4ng h\u00e0i l\u00f2ng","content":"M\u00ecnh \u0111\u1eb7t mua s\u1ea3n ph\u1ea9m n\u00e0y h\u00f4m 4\/4, ng\u00e0y 5\/4 m\u00ecnh nh\u1eadn \u0111\u01b0\u1ee3c h\u00e0ng, kh\u00f4ng h\u1ec1 c\u00f3 qu\u00e0 t\u1eb7ng k\u00e8m nh\u01b0 qu\u1ea3ng c\u00e1o, c\u1ea3 2 s\u1ea3n ph\u1ea9m \u0111\u1ec1u nh\u01b0 th\u1ebf. \u0110\u00e3 ch\u1ea5p nh\u1eadn mua gi\u00e1 cao h\u01a1n *** \u0111\u1ec3 nh\u1eadn \u0111\u01b0\u1ee3c t\u00fai t\u1eb7ng k\u00e8m m\u00e0 ko c\u00f3 th\u00ec kh\u00f4ng \u1ed5n r\u1ed3i. Tiki gi\u1ea3i quy\u1ebft tr\u01b0\u1eddng h\u1ee3p n\u00e0y cho m\u00ecnh.","status":"approved","thank_count":1,"score":2.80092593,"new_score":0.16990926000000001,"customer_id":805389,"comment_count":3,"rating":1,"images":[{"id":4178608,"full_path":"https:\/\/salt.tikicdn.com\/ts\/review\/22\/b0\/3f\/a13088711284fb3416a0724831614440.jpg","status":"approved"}],"thanked":false,"created_at":1680703632,"created_by":{"id":805389,"name":"Ng\u00f4 Th\u1ea3o T\u00e2m","full_name":"Ng\u00f4 Th\u1ea3o T\u00e2m","region":null,"avatar_url":"\/\/tiki.vn\/assets\/img\/avatar.png","created_time":"2015-09-10 00:25:47","group_id":8,"purchased":true,"purchased_at":1680588958,"contribute_info":{"id":805389,"name":"Ng\u00f4 Th\u1ea3o T\u00e2m","avatar":"\/\/tiki.vn\/assets\/img\/avatar.png","summary":{"joined_time":"\u0110\u00e3 tham gia 10 n\u0103m","total_review":13,"total_thank":14}}},"suggestions":[],"attributes":["Mua t\u1eeb nh\u00e0 b\u00e1n Tiki Trading"],"product_attributes":[],"spid":72711796,"is_photo":true,"seller":{"id":1,"name":"Tiki Trading","logo":"https:\/\/vcdn.tikicdn.com\/ts\/seller\/ee\/fa\/a0\/98f3f134f85cff2c6972c31777629aa0.png"},"product_id":72711795,"timeline":{"review_created_date":"2023-04-05 21:07:12","delivery_date":"2023-04-05 08:45:56","current_date":"2025-05-23 22:50:42","content":"\u0110\u00e3 d\u00f9ng 1 ng\u00e0y","explain":"Khi vi\u1ebft \u0111\u00e1nh gi\u00e1, kh\u00e1ch h\u00e0ng \u0111\u00e3 d\u00f9ng s\u1ea3n ph\u1ea9m 1 ng\u00e0y."},"vote_attributes":{"agree":[],"disagree":[]},"delivery_rating":[]},{"id":17927295,"title":"C\u1ef1c k\u00ec h\u00e0i l\u00f2ng","content":"L\u1ea7n \u0111\u1ea7u ti\u00ean s\u1eed d\u1ee5ng s\u1ea3n ph\u1ea9m c\u1ee7a Hadalabo r\u1ea5t c\u00f3 thi\u1ec7n c\u1ea3m. \nD\u01b0\u1ee1ng \u1ea9m d\u1ea1ng gel d\u1ec5 th\u1ea9m th\u1ea5u v\u00e0 r\u1ea5t nh\u1eb9 m\u1eb7t, tho\u00e1ng da, ph\u00f9 h\u1ee3p d\u00f9ng trong m\u00f9a h\u00e8 n\u1eafng n\u00f3ng. Hi\u1ec7u qu\u1ea3 d\u01b0\u1ee1ng \u1ea9m r\u1ea5t \u1ed5n, da c\u0103ng m\u01b0\u1edbt. \nShipper giao h\u00e0ng nhi\u1ec7t t\u00ecnh, t\u00ecnh tr\u1ea1ng h\u00e0ng ho\u00e1 t\u1ed1t. 5*","status":"approved","thank_count":2,"score":0.0031795199999999999,"new_score":0.16616923,"customer_id":23987028,"comment_count":0,"rating":5,"images":[{"id":3927554,"full_path":"https:\/\/salt.tikicdn.com\/ts\/review\/88\/c8\/4d\/a70e2fcc681865f9abf7969085963c4a.jpg","status":"approved"}],"thanked":false,"created_at":1665463169,"created_by":{"id":23987028,"name":"T\u01b0\u1eddng Vi","full_name":"T\u01b0\u1eddng Vi","region":null,"avatar_url":"\/\/tiki.vn\/assets\/img\/avatar.png","created_time":"2021-10-10 00:11:59","group_id":8,"purchased":true,"purchased_at":1664906757,"contribute_info":{"id":23987028,"name":"T\u01b0\u1eddng Vi","avatar":"\/\/tiki.vn\/assets\/img\/avatar.png","summary":{"joined_time":"\u0110\u00e3 tham gia 4 n\u0103m","total_review":17,"total_thank":2}}},"suggestions":[],"attributes":["Mua t\u1eeb nh\u00e0 b\u00e1n Tiki Trading"],"product_attributes":[],"spid":72711796,"is_photo":true,"seller":{"id":1,"name":"Tiki Trading","logo":"d1\/3f\/ae\/13ce3d83ab6b6c5e77e6377ad61dc4a5.jpg"},"product_id":72711795,"timeline":{"review_created_date":"2022-10-11 11:39:29","delivery_date":"2022-10-06 16:56:56","current_date":"2025-05-23 22:50:42","content":"\u0110\u00e3 d\u00f9ng 5 ng\u00e0y","explain":"Khi vi\u1ebft \u0111\u00e1nh gi\u00e1, kh\u00e1ch h\u00e0ng \u0111\u00e3 d\u00f9ng s\u1ea3n ph\u1ea9m 5 ng\u00e0y."},"vote_attributes":{"agree":[],"disagree":[]},"delivery_rating":[]}],"paging":{"total":123,"per_page":2,"current_page":1,"last_page":62,"from":1,"to":2},"sort_options":[[{"label":"H\u1eefu \u00edch","value":"score|desc"},{"label":"M\u1edbi nh\u1ea5t","value":"id|desc"},{"label":"C\u00f3 h\u00ecnh \u1ea3nh","value":"has_image"}],[{"label":"T\u1ea5t c\u1ea3 kh\u00e1ch h\u00e0ng","value":"customer|all"},{"label":"Kh\u00e1ch \u0111\u00e3 mua h\u00e0ng","value":"bought"}],[{"label":"T\u1ea5t c\u1ea3 sao","value":"stars|all"},{"label":"5 sao","value":"stars|5"},{"label":"4 sao","value":"stars|4"},{"label":"3 sao","value":"stars|3"},{"label":"2 sao","value":"stars|2"},{"label":"1 sao","value":"stars|1"},{"label":"H\u00e0i l\u00f2ng","value":"stars|4|5"},{"label":"Ch\u01b0a h\u00e0i l\u00f2ng","value":"stars|1|2|3"}]],"exclude_image":false,"attribute_vote_summary":[]}
# 

import os
import json
import requests
from datetime import datetime
from typing import List, Dict, Any
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from env import env

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = f"postgresql://{env.DB_USER}:{env.DB_PASSWORD}@{env.DB_HOST}:{env.DB_PORT}/{env.DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def fetch_reviews(product_id: int, page: int = 1, limit: int = 20) -> Dict[str, Any]:
    """Fetch reviews from Tiki API for a specific product"""
    url = f"https://tiki.vn/api/v2/reviews?limit={limit}&page={page}&product_id={product_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching reviews for product {product_id}: {str(e)}")
        return None

def insert_review(db, review_data: Dict[str, Any], product_id: int) -> None:
    """Insert review data directly using raw SQL"""
    query = text("""
        INSERT INTO reviews (review_id, product_id, customer_id, rating, comment, review_date, likes, dislikes)
        VALUES (:review_id, :product_id, :customer_id, :rating, :comment, :review_date, :likes, :dislikes)
        ON CONFLICT (review_id) DO NOTHING
    """)
    
    try:
        db.execute(query, {
            "review_id": review_data["id"],
            "product_id": product_id,
            "customer_id": 1,  # Default customer ID
            "rating": review_data["rating"],
            "comment": review_data["content"],
            "review_date": datetime.fromtimestamp(review_data["created_at"]),
            "likes": review_data["thank_count"],
            "dislikes": 0  # Default value
        })
    except Exception as e:
        print(f"Error inserting review {review_data.get('id')}: {str(e)}")
        raise

def crawl_reviews_for_product(product_id: int, db) -> None:
    """Crawl all reviews for a specific product"""
    page = 1
    total_reviews = 0
    
    while True:
        print(f"Fetching page {page} for product {product_id}...")
        response_data = fetch_reviews(product_id, page)
        
        if not response_data or "data" not in response_data:
            break
            
        reviews = response_data["data"]
        if not reviews:
            break
            
        # Process each review
        for review_data in reviews:
            try:
                insert_review(db, review_data, product_id)
                total_reviews += 1
            except Exception as e:
                print(f"Error processing review {review_data.get('id')}: {str(e)}")
                continue
        
        # Commit after each page
        try:
            db.commit()
        except Exception as e:
            print(f"Error committing reviews for product {product_id}: {str(e)}")
            db.rollback()
        
        # Check if we've reached the last page
        if page >= response_data["paging"]["last_page"]:
            break
            
        page += 1
        # time.sleep(1)  # Be nice to the API
    
    print(f"Completed crawling {total_reviews} reviews for product {product_id}")

def get_product_ids(db) -> List[int]:
    """Get list of product IDs from database using raw SQL"""
    query = text("SELECT product_id FROM products")
    result = db.execute(query)
    return [row[0] for row in result]

def main():
    """Main function to crawl reviews for all products"""
    db = next(get_db())
    
    try:
        # Get only product IDs from database
        product_ids = get_product_ids(db)
        
        for product_id in product_ids:
            print(f"\nProcessing product {product_id}...")
            crawl_reviews_for_product(product_id, db)
            # time.sleep(2)  # Be nice to the API between products
            
    except Exception as e:
        print(f"Error in main process: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 