import asyncio
from shop_chat.shop_manager import ShopManager
from db import get_db  # Đường dẫn đúng tuỳ dự án của bạn


# Nếu bạn có context async, ví dụ trong FastAPI route thì chỉ cần await
async def main():
    # Giả sử bạn dùng SQLAlchemy Session thông thường:
    db = next(get_db())
    shop_id = 1
    shop_manager = ShopManager(db=db, shop_id=shop_id)

    message = "Shop tôi có bao nhiêu sản phẩm?"
    response = {
        "agent": "ProductManagementAgent",
        "query": "Thống kê tổng số sản phẩm hiện có trong shop",
    }

    result = shop_manager.process_chat_message(message, response, shop_id)
    if asyncio.iscoroutine(result):
        result = await result
    print(result)


# Nếu gọi từ script thường
if __name__ == "__main__":
    asyncio.run(main())
