import re
from bs4 import BeautifulSoup
from unidecode import unidecode
from services.products import ProductServices

def normalize_text(text: str) -> str:
    """
    Chuẩn hóa khoảng trắng, loại bỏ dấu tiếng Việt (nếu cần), bỏ ký tự dư thừa.
    """
    text = re.sub(r"\s+", " ", text)            # Gom khoảng trắng
    text = re.sub(r"\.+", ".", text)            # Gom dấu chấm liên tiếp
    return text.strip()

def extract_text_from_html(html_content: str) -> str:
    """
    Loại bỏ HTML tags và trả về plain text.
    """
    soup = BeautifulSoup(html_content or "", "html.parser")
    return soup.get_text(separator=" ", strip=True)

def extract_expiration_date(text: str) -> str:
    """
    Tìm và tách 'Hạn sử dụng' ra khỏi mô tả.
    """
    match = re.search(r"Hạn sử dụng:\s*(\d{4}-\d{2}-\d{2})", text)
    if match:
        return match.group(1)
    return ""

def remove_time_format(text: str) -> str:
    """
    Loại bỏ các chuỗi thời gian theo định dạng HH:MM:SS (ví dụ: 00:00:00).
    """
    return re.sub(r"\d{2}:\d{2}:\d{2}", "", text).strip()

def preprocess_product(product_data: dict) -> str:
    """
    Chuẩn hóa thông tin sản phẩm để sẵn sàng tạo embedding.
    """
    product = product_data.get("product", {})

    name = product.name.strip()
    short_description = product.short_description.strip()
    description_html = product.description

    brand_name = (
        product_data["brand"][0].brand_name.strip()
        if product_data.get("brand")
        else ""
    )
    seller_name = (
        product_data.get("seller", [{}])[0].seller_name.strip()
        if product_data.get("seller")
        else ""
    )
    category_name = (
        product_data.get("category", [{}])[0].name.strip()
        if product_data.get("category")
        else ""
    )

    full_description = extract_text_from_html(description_html)

    # Tìm và tách "Hạn sử dụng"
    expiration_date = extract_expiration_date(full_description)
    
    # Xóa phần "Hạn sử dụng" khỏi mô tả nếu có
    if expiration_date:
        full_description = re.sub(r"Hạn sử dụng:\s*\d{4}-\d{2}-\d{2}", "", full_description).strip()

    # Loại bỏ các định dạng thời gian không cần thiết
    full_description = remove_time_format(full_description)

    # Bỏ trùng nội dung nếu tóm tắt đã nằm trong mô tả chi tiết
    if short_description and short_description in full_description:
        short_description = ""

    parts = [
        f"Tên sản phẩm: {name}",
        f"Danh mục: {category_name}" if category_name else "",
        f"Thương hiệu: {brand_name}" if brand_name else "",
        f"Người bán: {seller_name}" if seller_name else "",
        f"Mô tả ngắn: {short_description}" if short_description else "",
        f"Mô tả chi tiết: {full_description}" if full_description else "",
    ]

    full_text = ". ".join([p for p in parts if p]) + "."
    return normalize_text(full_text)