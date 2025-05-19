CREATE TABLE "products" (
  "product_id" integer PRIMARY KEY,
  "name" varchar,
  "product_short_url" varchar,
  "description" text,
  "short_description" text,
  "price" decimal,
  "original_price" decimal,
  "discount" decimal,
  "discount_rate" integer,
  "sku" varchar,
  "review_text" varchar,
  "quantity_sold" integer,
  "rating_average" decimal,
  "review_count" integer,
  "order_count" integer,
  "favourite_count" integer,
  "thumbnail_url" varchar,
  "category_id" integer,
  "brand_id" integer,
  "seller_id" integer,
  "shippable" boolean,
  "availability" integer,
  "created_at" timestamp,
  "updated_at" timestamp
);

CREATE TABLE "categories" (
  "category_id" integer PRIMARY KEY,
  "name" varchar,
  "path" varchar
);

CREATE TABLE "brands" (
  "brand_id" integer PRIMARY KEY,
  "brand_name" varchar,
  "brand_slug" varchar,
  "brand_country" varchar
);

CREATE TABLE "sellers" (
  "seller_id" integer PRIMARY KEY,
  "seller_name" varchar,
  "seller_type" varchar,
  "seller_link" varchar,
  "seller_logo_url" varchar,
  "seller_store_id" integer,
  "seller_is_best_store" boolean,
  "is_seller" boolean,
  "is_seller_in_chat_whitelist" boolean,
  "is_offline_installment_supported" boolean,
  "store_rating" decimal,
  "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "product_images" (
  "id" SERIAL PRIMARY KEY,
  "product_id" integer,
  "variant_id" integer,
  "base_url" varchar,
  "large_url" varchar,
  "medium_url" varchar,
  "small_url" varchar,
  "thumbnail_url" varchar,
  "position" integer,
  "is_gallery" boolean
);

CREATE TABLE "warranties" (
  "warranty_id" SERIAL PRIMARY KEY,
  "product_id" integer,
  "name" varchar,
  "warranty_period" varchar,
  "warranty_form" varchar,
  "warranty_location" varchar,
  "policy_info" varchar
);

CREATE TABLE "product_variants" (
  "id" integer PRIMARY KEY,
  "product_id" integer,
  "sku" varchar,
  "name" varchar,
  "price" decimal,
  "original_price" decimal,
  "inventory_status" varchar,
  "thumbnail_url" varchar,
  "option1" varchar
);

CREATE TABLE "customers" (
  "customer_id" integer PRIMARY KEY,
  "customer_fname" varchar,
  "customer_lname" varchar,
  "customer_mail" varchar,
  "customer_address" varchar,
  "customer_phone" varchar,
  "customer_dob" date,
  "customer_gender" varchar
);

CREATE TABLE "orders" (
  "order_id" integer PRIMARY KEY,
  "customer_id" integer,
  "order_status" varchar,
  "total_amount" decimal,
  "order_date" timestamp,
  "payment_method" varchar,
  "delivery_method" varchar,
  "delivery_fee" decimal,
  "discount_amount" decimal,
  "transaction_code" varchar
);

CREATE TABLE "order_details" (
  "order_detail_id" integer PRIMARY KEY,
  "order_id" integer,
  "product_id" integer,
  "variant_id" integer,
  "quantity" integer,
  "unit_price" decimal,
  "discount" decimal
);

CREATE TABLE "inventory" (
  "inventory_id" integer PRIMARY KEY,
  "product_id" integer,
  "variant_id" integer,
  "stock_quantity" integer,
  "restock_date" timestamp
);

CREATE TABLE "shipping_info" (
  "shipping_id" integer PRIMARY KEY,
  "order_id" integer,
  "shipping_status" varchar,
  "estimated_delivery" timestamp,
  "tracking_number" varchar,
  "carrier" varchar
);

CREATE TABLE "discounts" (
  "discount_id" integer PRIMARY KEY,
  "discount_name" varchar,
  "discount_rate" decimal,
  "start_date" timestamp,
  "end_date" timestamp,
  "is_active" boolean,
  "min_purchase_amount" decimal,
  "max_discount_amount" decimal
);

CREATE TABLE "product_discounts" (
  "product_id" integer,
  "discount_id" integer,
  PRIMARY KEY ("product_id", "discount_id")
);

CREATE TABLE "transactions" (
  "transaction_code" varchar PRIMARY KEY,
  "order_id" integer,
  "customer_id" integer,
  "amount" decimal,
  "payment_method" varchar,
  "payment_status" varchar,
  "transaction_date" timestamp,
  "is_successful" boolean
);

CREATE TABLE "buy_history" (
  "buy_history_id" integer PRIMARY KEY,
  "customer_id" integer,
  "product_id" integer,
  "order_id" integer,
  "purchase_date" timestamp,
  "quantity" integer,
  "price" decimal
);

CREATE TABLE "reviews" (
  "review_id" SERIAL PRIMARY KEY,
  "product_id" integer,
  "customer_id" integer,
  "rating" integer,
  "comment" text,
  "review_date" timestamp,
  "likes" integer,
  "dislikes" integer
);

CREATE TABLE "wishlists" (
  "wishlist_id" SERIAL PRIMARY KEY,
  "customer_id" integer,
  "name" varchar,
  "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "wishlist_items" (
  "wishlist_id" integer,
  "product_id" integer,
  "added_at" timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("wishlist_id", "product_id")
);

CREATE TABLE "shopping_carts" (
  "cart_id" SERIAL PRIMARY KEY,
  "customer_id" integer,
  "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "cart_items" (
  "cart_id" integer,
  "product_id" integer,
  "variant_id" integer,
  "quantity" integer,
  "added_at" timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("cart_id", "product_id", "variant_id")
);

CREATE TABLE "coupons" (
  "coupon_id" SERIAL PRIMARY KEY,
  "code" varchar UNIQUE,
  "description" text,
  "discount_type" varchar,
  "discount_value" decimal,
  "min_purchase" decimal,
  "max_discount" decimal,
  "start_date" timestamp,
  "end_date" timestamp,
  "is_active" boolean,
  "usage_limit" integer,
  "usage_count" integer DEFAULT 0
);

CREATE TABLE "customer_coupons" (
  "customer_id" integer,
  "coupon_id" integer,
  "is_used" boolean DEFAULT false,
  "used_at" timestamp,
  PRIMARY KEY ("customer_id", "coupon_id")
);

CREATE TABLE "customer_addresses" (
  "address_id" SERIAL PRIMARY KEY,
  "customer_id" integer,
  "address_line1" varchar,
  "address_line2" varchar,
  "city" varchar,
  "state" varchar,
  "postal_code" varchar,
  "country" varchar,
  "is_default" boolean,
  "address_type" varchar
);

CREATE TABLE "product_tags" (
  "tag_id" SERIAL PRIMARY KEY,
  "name" varchar UNIQUE
);

CREATE TABLE "product_tag_relations" (
  "product_id" integer,
  "tag_id" integer,
  PRIMARY KEY ("product_id", "tag_id")
);

CREATE TABLE "shops" (
  "seller_id" integer PRIMARY KEY,
  "username" varchar UNIQUE NOT NULL,
  "password" varchar NOT NULL,
  "name" varchar NOT NULL,
  "mail" varchar UNIQUE,
  "address" varchar,
  "phone" varchar,
  "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP
);

-- New tables

CREATE TABLE "product_embeddings" (
  "embedding_id" SERIAL PRIMARY KEY,
  "product_id" integer NOT NULL,
  "embedding_vector" vector(384),
  "embedding_type" varchar DEFAULT 'description',
  "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "product_attributes" (
  "attribute_id" SERIAL PRIMARY KEY,
  "product_id" integer NOT NULL,
  "attribute_name" varchar NOT NULL,
  "attribute_value" varchar NOT NULL,
  "is_filterable" boolean DEFAULT false,
  "is_searchable" boolean DEFAULT true,
  "display_order" integer DEFAULT 0
);

CREATE TABLE "product_specifications" (
  "specification_id" SERIAL PRIMARY KEY,
  "product_id" integer NOT NULL,
  "specification_name" varchar NOT NULL,
  "specification_value" varchar NOT NULL,
  "specification_group" varchar,
  "display_order" integer DEFAULT 0
);

CREATE TABLE "users" (
  "user_id" SERIAL PRIMARY KEY,
  "username" varchar UNIQUE NOT NULL,
  "email" varchar UNIQUE NOT NULL,
  "password_hash" varchar NOT NULL,
  "salt" varchar NOT NULL,
  "is_active" boolean DEFAULT true,
  "is_admin" boolean DEFAULT false,
  "last_login" timestamp,
  "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "user_roles" (
  "role_id" SERIAL PRIMARY KEY,
  "role_name" varchar UNIQUE NOT NULL,
  "role_description" varchar,
  "created_at" timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "user_role_assignments" (
  "user_id" integer NOT NULL,
  "role_id" integer NOT NULL,
  "assigned_at" timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("user_id", "role_id")
);

CREATE TABLE "sessions" (
  "session_id" varchar PRIMARY KEY,
  "user_id" integer NOT NULL,
  "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
  "expires_at" timestamp NOT NULL,
  "ip_address" varchar,
  "user_agent" varchar
);

CREATE TABLE "product_imports" (
  "import_id" SERIAL PRIMARY KEY,
  "source" varchar NOT NULL,
  "import_date" timestamp DEFAULT CURRENT_TIMESTAMP,
  "import_status" varchar DEFAULT 'pending',
  "total_products" integer DEFAULT 0,
  "successful_imports" integer DEFAULT 0,
  "failed_imports" integer DEFAULT 0,
  "import_log" text
);

CREATE TABLE "search_logs" (
  "search_id" SERIAL PRIMARY KEY,
  "user_id" integer,
  "customer_id" integer,
  "search_query" varchar NOT NULL,
  "search_timestamp" timestamp DEFAULT CURRENT_TIMESTAMP,
  "results_count" integer,
  "clicked_product_id" integer,
  "session_id" varchar
);

COMMENT ON COLUMN "product_variants"."option1" IS 'Variant option value';

-- Product relationships
ALTER TABLE "products" ADD FOREIGN KEY ("category_id") REFERENCES "categories" ("category_id");
ALTER TABLE "products" ADD FOREIGN KEY ("brand_id") REFERENCES "brands" ("brand_id");
ALTER TABLE "products" ADD FOREIGN KEY ("seller_id") REFERENCES "sellers" ("seller_id");

-- Category hierarchy
ALTER TABLE "categories" ADD FOREIGN KEY ("parent_id") REFERENCES "categories" ("category_id");

-- Product variants and images
ALTER TABLE "product_variants" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("product_id");
ALTER TABLE "product_images" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("product_id");
ALTER TABLE "product_images" ADD FOREIGN KEY ("variant_id") REFERENCES "product_variants" ("id");

-- Product warranties
ALTER TABLE "warranties" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("product_id");

-- Reviews
ALTER TABLE "reviews" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("product_id");
ALTER TABLE "reviews" ADD FOREIGN KEY ("customer_id") REFERENCES "customers" ("customer_id");

-- Order relationships
ALTER TABLE "orders" ADD FOREIGN KEY ("customer_id") REFERENCES "customers" ("customer_id");
ALTER TABLE "order_details" ADD FOREIGN KEY ("order_id") REFERENCES "orders" ("order_id");
ALTER TABLE "order_details" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("product_id");
ALTER TABLE "order_details" ADD FOREIGN KEY ("variant_id") REFERENCES "product_variants" ("id");

-- Inventory management
ALTER TABLE "inventory" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("product_id");
ALTER TABLE "inventory" ADD FOREIGN KEY ("variant_id") REFERENCES "product_variants" ("id");

-- Shipping information
ALTER TABLE "shipping_info" ADD FOREIGN KEY ("order_id") REFERENCES "orders" ("order_id");

-- Discount relationships
ALTER TABLE "product_discounts" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("product_id");
ALTER TABLE "product_discounts" ADD FOREIGN KEY ("discount_id") REFERENCES "discounts" ("discount_id");

-- Transaction relationships
ALTER TABLE "transactions" ADD FOREIGN KEY ("order_id") REFERENCES "orders" ("order_id");
ALTER TABLE "transactions" ADD FOREIGN KEY ("customer_id") REFERENCES "customers" ("customer_id");

-- Buy history relationships
ALTER TABLE "buy_history" ADD FOREIGN KEY ("customer_id") REFERENCES "customers" ("customer_id");
ALTER TABLE "buy_history" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("product_id");
ALTER TABLE "buy_history" ADD FOREIGN KEY ("order_id") REFERENCES "orders" ("order_id");

-- Wishlist relationships
ALTER TABLE "wishlists" ADD FOREIGN KEY ("customer_id") REFERENCES "customers" ("customer_id");
ALTER TABLE "wishlist_items" ADD FOREIGN KEY ("wishlist_id") REFERENCES "wishlists" ("wishlist_id");
ALTER TABLE "wishlist_items" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("product_id");

-- Shopping cart relationships
ALTER TABLE "shopping_carts" ADD FOREIGN KEY ("customer_id") REFERENCES "customers" ("customer_id");
ALTER TABLE "cart_items" ADD FOREIGN KEY ("cart_id") REFERENCES "shopping_carts" ("cart_id");
ALTER TABLE "cart_items" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("product_id");
ALTER TABLE "cart_items" ADD FOREIGN KEY ("variant_id") REFERENCES "product_variants" ("id");

-- Coupon relationships
ALTER TABLE "customer_coupons" ADD FOREIGN KEY ("customer_id") REFERENCES "customers" ("customer_id");
ALTER TABLE "customer_coupons" ADD FOREIGN KEY ("coupon_id") REFERENCES "coupons" ("coupon_id");

-- Customer address relationships
ALTER TABLE "customer_addresses" ADD FOREIGN KEY ("customer_id") REFERENCES "customers" ("customer_id");

-- Product tags relationships
ALTER TABLE "product_tag_relations" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("product_id");
ALTER TABLE "product_tag_relations" ADD FOREIGN KEY ("tag_id") REFERENCES "product_tags" ("tag_id");

-- Shop relationships
ALTER TABLE "shops" ADD FOREIGN KEY ("seller_id") REFERENCES "sellers" ("seller_id");

-- Foreign keys for new tables
ALTER TABLE "product_embeddings" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("product_id");
ALTER TABLE "product_attributes" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("product_id");
ALTER TABLE "product_specifications" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("product_id");
ALTER TABLE "user_role_assignments" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("user_id");
ALTER TABLE "user_role_assignments" ADD FOREIGN KEY ("role_id") REFERENCES "user_roles" ("role_id");
ALTER TABLE "sessions" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("user_id");
ALTER TABLE "search_logs" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("user_id") ON DELETE SET NULL;
ALTER TABLE "search_logs" ADD FOREIGN KEY ("customer_id") REFERENCES "customers" ("customer_id") ON DELETE SET NULL;
ALTER TABLE "search_logs" ADD FOREIGN KEY ("clicked_product_id") REFERENCES "products" ("product_id") ON DELETE SET NULL;
ALTER TABLE "search_logs" ADD FOREIGN KEY ("session_id") REFERENCES "sessions" ("session_id") ON DELETE SET NULL;