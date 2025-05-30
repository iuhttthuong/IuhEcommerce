### get atribute
def get_attribute_value(data, attribute_code):
    # Kiểm tra nếu data là list thì duyệt qua từng item
    if isinstance(data, list):
        for item in data:
            result = get_attribute_value(item, attribute_code)
            if result is not None:
                return result
        return None
    
    # Kiểm tra nếu data là dict và có key 'attributes'
    if isinstance(data, dict) and 'attributes' in data:
        for attr in data['attributes']:
            if attr['code'] == attribute_code:
                return attr['value']
    
    return None       

## extract_category_info
def extract_category_info(category_data):
    result = []
    full_category_id = ""  # Dùng để lưu category_id dạng phân cấp
    
    for index, item in enumerate(category_data, start=1):
        # Xử lý url để lấy path
        url = item['url']
        if url.startswith('http'):
            path_parts = url.split('/')[3:]
            path = '/' + '/'.join(path_parts)
        else:
            path = url
        
        # Xác định level (tăng dần từ 1 đến 4)
        level = index
        
        # Xử lý category_id dạng phân cấp
        if full_category_id:
            full_category_id += "/" + str(item['category_id'])
        else:
            full_category_id = str(item['category_id'])
        
        # Parent_id sẽ là category_id của item trước đó
        parent_id = category_data[index-2]['category_id'] if index > 1 else 0
        
        category_info = {
            'category_id': full_category_id,  # Dạng "1883.53050.2363.0"
            'name': item['name'],
            'parent_id': parent_id,
            'level': level,
            'path': path
        }
        result.append(category_info)
    
    return result

## get_last_category_id
def get_last_category_id(categories_info):
    """
    Lấy category_id cuối cùng từ danh sách categories_info
    
    Args:
        categories_info (list): Danh sách kết quả từ hàm extract_category_info()
    
    Returns:
        str: category_id cuối cùng hoặc None nếu danh sách rỗng
    """
    if not categories_info:
        return None
    
    # Lấy phần tử cuối cùng trong danh sách
    last_category = categories_info[-1]
    return last_category['category_id']

## warranty value
def get_value_by_name(items, target_name):
    for item in items:
        if item["name"] == target_name:
            return item.get("value")
    return None

# warranty_url
def extract_url(items):
    for item in items:
        if 'url' in item and item['url']:  # Kiểm tra nếu có key 'url' và giá trị không rỗng
            return item['url']
    return None  # Trả về None nếu không tìm thấy URL

