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
  "parent_id" integer,
  "level" integer,
  "path" varchar
);

CREATE TABLE "brands" (
  "brand_id" integer PRIMARY KEY,
  "brand_name" varchar,
  "brand_slug" varchar,
  "brand_country" varchar,
  "is_top_brand" boolean
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
  "id" integer PRIMARY KEY,
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
  "warranty_id" integer PRIMARY KEY,
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
  "inventory_id" integer PRIMARY KEY,"product_id" integer,
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