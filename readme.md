``` Vị trí Thư Mục ```
.env chứ các key, api, db, ....
env.py load 



``` Hướng dẫn sử dụng ```
- set up môi trường cho docker: export $(grep -v '^#' .env | xargs)

 
``` scrip ```

-   Set up môi trường cho docker: export $(grep -v '^#' .env | xargs)
-   Chuyển sang ubun tu : "wsl -d ubuntu"
-   Chạy poetry install để cài thư viện
-   chạy poetry shell để acivate môi trương ảoảo
-    "docker compose up -d"
-   init database: alembic upgrade head
-   chạy 2 file importdata/pre.py và importdata/pre_product.py để parsing data
-   chạy file importdata/cre để tạo dữ liệu
-   chạy fastapi dev app.py để vào swagger


