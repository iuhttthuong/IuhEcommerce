#!/bin/bash

# Chạy câu lệnh SQL tạo bảng từ file `create_shops_table.sql`
docker exec -i postgres psql -U E_commerce_chatbot -d E_commerce_chatbot < scripts/create_shops_table.sql

# Copy file insert vào container và chạy nó
docker cp scripts/insert_shop_data.sql postgres:/insert_shop_data.sql
docker exec -i postgres psql -U E_commerce_chatbot -d E_commerce_chatbot -f /insert_shop_data.sql
