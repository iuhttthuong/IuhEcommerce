import re
from bs4 import BeautifulSoup
from unidecode import unidecode
from repositories.products import ProductRepositories

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
    price = product.price
    original_price = product.original_price
    discount_rate = product.discount_rate
    rating_average = product.rating_average
    review_count = product.review_count

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

    # Extract specifications if available
    specifications = []
    if product_data.get("specifications"):
        for spec in product_data.get("specifications", []):
            spec_name = spec.specification_name
            spec_value = spec.specification_value
            specifications.append(f"{spec_name}: {spec_value}")
    
    specifications_text = ". ".join(specifications)

    # Extract product attributes if available
    attributes = []
    if product_data.get("attributes"):
        for attr in product_data.get("attributes", []):
            attr_name = attr.attribute_name
            attr_value = attr.attribute_value
            attributes.append(f"{attr_name}: {attr_value}")
    
    attributes_text = ". ".join(attributes)

    # Extract warranty information if available
    warranty_info = ""
    if product_data.get("warranty"):
        warranty = product_data.get("warranty")[0]
        warranty_period = warranty.warranty_period
        warranty_form = warranty.warranty_form
        warranty_location = warranty.warranty_location
        warranty_info = f"Bảo hành: {warranty_period}, Hình thức: {warranty_form}, Địa điểm: {warranty_location}"

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

    # Get related tags if available
    tags = []
    if product_data.get("tags"):
        for tag in product_data.get("tags", []):
            tags.append(tag.name)
    
    tags_text = ", ".join(tags)

    # Pricing and discount information
    pricing_info = f"Giá: {price}, Giá gốc: {original_price}, Giảm giá: {discount_rate}%"
    
    # Rating information
    rating_info = f"Đánh giá: {rating_average}/5, Số lượng đánh giá: {review_count}"

    parts = [
        f"Tên sản phẩm: {name}",
        f"Danh mục: {category_name}" if category_name else "",
        f"Thương hiệu: {brand_name}" if brand_name else "",
        f"Người bán: {seller_name}" if seller_name else "",
        f"Mô tả ngắn: {short_description}" if short_description else "",
        f"Mô tả chi tiết: {full_description}" if full_description else "",
        f"Thông số kỹ thuật: {specifications_text}" if specifications_text else "",
        f"Thuộc tính sản phẩm: {attributes_text}" if attributes_text else "",
        f"Thông tin bảo hành: {warranty_info}" if warranty_info else "",
        pricing_info,
        rating_info,
        f"Tags: {tags_text}" if tags_text else ""
    ]

    full_text = ". ".join([p for p in parts if p]) + "."
    return normalize_text(full_text)

def preprocess_faq(faq_data: dict) -> str:
    """
    Chuẩn hóa thông tin FAQ để sẵn sàng tạo embedding.
    """
    # Kiểm tra nếu đầu vào là đối tượng FQAModel
    if hasattr(faq_data, 'question') and hasattr(faq_data, 'answer'):
        question = faq_data.question.strip()
        answer = faq_data.answer.strip()
    else:
        # Trường hợp là dictionary
        question = faq_data.get("question", "").strip()
        answer = faq_data.get("answer", "").strip()
    
    full_text = f"Câu hỏi: {question}. Trả lời: {answer}"
    return normalize_text(full_text)

def preprocess_review(review_data: dict) -> str:
    """
    Chuẩn hóa thông tin đánh giá sản phẩm để sẵn sàng tạo embedding.
    """
    product_id = review_data.get("product_id", "")
    product_name = review_data.get("product_name", "")
    rating = review_data.get("rating", 0)
    comment = review_data.get("comment", "").strip()
    
    full_text = f"Sản phẩm: {product_name}. ID: {product_id}. Đánh giá: {rating}/5. Nhận xét: {comment}"
    return normalize_text(full_text)

def preprocess_category(category_data: dict) -> str:
    """
    Chuẩn hóa thông tin danh mục để sẵn sàng tạo embedding.
    """
    # Kiểm tra nếu đầu vào là đối tượng Category
    if hasattr(category_data, 'name') and hasattr(category_data, 'path'):
        name = category_data.name.strip() if category_data.name else ""
        path = category_data.path.strip() if category_data.path else ""
        # Category không có thuộc tính parent_name hoặc parent_id
        parent_name = ""
    else:
        # Trường hợp là dictionary
        name = category_data.get("name", "").strip()
        path = category_data.get("path", "").strip()
        parent_name = category_data.get("parent_name", "").strip()
    
    full_text = f"Danh mục: {name}. Đường dẫn: {path}"
    if parent_name:
        full_text = f"Danh mục: {name}. Danh mục cha: {parent_name}. Đường dẫn: {path}"
        
    return normalize_text(full_text)

def preprocess_chat(chat_data: dict) -> str:
    """
    Chuẩn hóa thông tin chat để sẵn sàng tạo embedding.
    """
    # Kiểm tra xem chat_data có thuộc tính messages hay không
    messages = chat_data.get("messages", [])
    conversation = []
    
    if messages:  # Nếu có messages trong chat_data
        for msg in messages:
            if isinstance(msg, dict):
                role = msg.get("role", "")
                content = msg.get("content", "").strip()
                conversation.append(f"{role}: {content}")
    
    # Thêm thông tin cơ bản của chat vào văn bản
    chat_id = chat_data.get("id", "")
    session_id = chat_data.get("session_id", "")
    user_id = chat_data.get("user_id", "")
    title = chat_data.get("title", "")
    # Ensure title is a string even if None
    title = title or ""
    title = title.strip()
    
    # Nếu không có nội dung conversation, dùng chỉ thông tin chat
    if not conversation:
        full_text = f"Chat ID: {chat_id}. Session: {session_id}. User: {user_id}. Title: {title}"
    else:
        # Kết hợp thông tin chat với nội dung conversation
        chat_info = f"Chat ID: {chat_id}. Session: {session_id}. User: {user_id}. Title: {title}"
        conversation_text = ". ".join(conversation)
        full_text = f"{chat_info}. Nội dung: {conversation_text}"
    
    return normalize_text(full_text)

def preprocess_search_log(search_data: dict) -> str:
    """
    Chuẩn hóa thông tin log tìm kiếm để sẵn sàng tạo embedding.
    """
    query = search_data.get("search_query", "").strip()
    clicked_product = search_data.get("clicked_product_name", "")
    
    full_text = f"Truy vấn tìm kiếm: {query}. Sản phẩm đã click: {clicked_product}"
    return normalize_text(full_text)