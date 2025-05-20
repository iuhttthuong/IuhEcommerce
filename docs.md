# TÀI LIỆU HỆ THỐNG AGENT IUH-ECOMMERCE

## 1. TỔNG QUAN

### 1.1. Giới Thiệu

Hệ thống Agent IUH-Ecommerce là một nền tảng thương mại điện tử thông minh được xây dựng trên FastAPI, tích hợp các agent AI để cung cấp trải nghiệm mua sắm và quản lý cửa hàng tối ưu. Hệ thống được thiết kế với hai luồng tương tác riêng biệt: một cho khách hàng và một cho cửa hàng, mỗi luồng có các agent chuyên biệt để xử lý các yêu cầu cụ thể.

### 1.2. Kiến Trúc Hệ Thống

#### 1.2.1. Các Thành Phần Chính
1. **API Layer**
   - FastAPI Framework
   - RESTful Endpoints
   - WebSocket Support
   - CORS Middleware

2. **Agent Layer**
   - Manager Agent
   - Orchestrator Agent
   - Specialized Agents
   - AutoGen Framework

3. **Data Layer**
   - PostgreSQL Database
   - Qdrant Vector DB
   - Redis Cache
   - Kafka Message Queue

4. **Integration Layer**
   - External APIs
   - Payment Gateways
   - Shipping Services
   - Analytics Tools

#### 1.2.2. Các Module Chính
1. **Customer Module**
   - Chat System
   - Product Search
   - Order Management
   - User Profile

2. **Shop Module**
   - Shop Management
   - Inventory Control
   - Order Processing
   - Analytics

3. **AI Module**
   - Natural Language Processing
   - Recommendation System
   - Sentiment Analysis
   - Product Comparison

### 1.3. Công Nghệ Sử Dụng

#### 1.3.1. Core Technologies
- **Backend Framework:** FastAPI 0.68.0+
- **Database:** PostgreSQL (SQLAlchemy 1.4.23+)
- **AI Framework:** AutoGen 0.2.0+
- **Message Queue:** Kafka
- **Vector Database:** Qdrant
- **Authentication:** JWT (python-jose)

#### 1.3.2. Các Thư Viện Chính
- **Web Server:** Uvicorn 0.15.0+
- **Database ORM:** SQLAlchemy, Alembic
- **Security:** Passlib, python-multipart
- **Environment:** python-dotenv
- **Data Validation:** Pydantic

### 1.4. API Endpoints

#### 1.4.1. Customer Endpoints
- `/api/customer/chat` - Hệ thống chat cho khách hàng
- `/api/customers` - Quản lý thông tin khách hàng
- `/api/customer/messages` - Quản lý tin nhắn
- `/api/products` - Quản lý sản phẩm
- `/api/search` - Tìm kiếm sản phẩm
- `/api/discounts` - Quản lý giảm giá
- `/api/product-discounts` - Giảm giá sản phẩm

#### 1.4.2. Shop Endpoints
- `/api/shops` - Quản lý cửa hàng
- `/api/shop/chat` - Hệ thống chat cho cửa hàng

#### 1.4.3. AI Agent Endpoints
- `/api/qdrant-agent` - Agent tìm kiếm vector
- `/api/manager` - Agent quản lý
- `/api/orchestrator` - Agent điều phối
- `/api/reviews` - Agent đánh giá
- `/api/recommendation` - Agent gợi ý
- `/api/product-comparison` - Agent so sánh sản phẩm
- `/api/product-info` - Agent thông tin sản phẩm
- `/api/search-discovery` - Agent tìm kiếm và khám phá
- `/api/user-profile` - Agent hồ sơ người dùng

#### 1.4.4. FAQ và Policy Endpoints
- `/api/faq-loader` - Tải FAQ
- `/api/fqas` - Quản lý FAQ
- `/api/policies-agent` - Agent chính sách

### 1.5. Tính Năng Chính

#### 1.5.1. Cho Khách Hàng
- Tìm kiếm sản phẩm thông minh
- Gợi ý sản phẩm cá nhân hóa
- So sánh sản phẩm
- Đánh giá và phản hồi
- Quản lý đơn hàng
- Hỗ trợ thanh toán

#### 1.5.2. Cho Cửa Hàng
- Quản lý sản phẩm và tồn kho
- Xử lý đơn hàng
- Phân tích kinh doanh
- Quản lý khuyến mãi
- Hỗ trợ khách hàng
- Báo cáo và thống kê

### 1.6. Bảo Mật và Xác Thực

#### 1.6.1. Xác Thực
- JWT Authentication
- Role-based Access Control
- API Key Management
- Session Management

#### 1.6.2. Bảo Mật
- CORS Protection
- Input Validation
- Data Encryption
- Rate Limiting

### 1.7. Monitoring và Logging

#### 1.7.1. Health Check
- Endpoint: `/health`
- Status Monitoring
- System Health
- Chat System Status

#### 1.7.2. Logging
- Request Logging
- Error Tracking
- Performance Monitoring
- Security Auditing

### 1.8. Deployment và Scaling

#### 1.8.1. Containerization
- Docker Support
- Docker Compose
- Multi-container Architecture
- Service Isolation

#### 1.8.2. Database Migration
- Alembic Migrations
- Version Control
- Rollback Support
- Data Integrity

### 1.9. Development và Testing

#### 1.9.1. Development Environment
- Local Development Setup
- Debug Mode
- Hot Reload
- Environment Variables

#### 1.9.2. Testing
- Unit Testing
- Integration Testing
- API Testing
- Performance Testing

### 1.10. Tương Lai và Mở Rộng

#### 1.10.1. Kế Hoạch Phát Triển
- AI Model Enhancement
- Performance Optimization
- Feature Expansion
- Security Updates

#### 1.10.2. Khả Năng Mở Rộng
- Microservices Architecture
- Load Balancing
- Horizontal Scaling
- Service Discovery

Hệ thống được thiết kế theo mô hình phân tầng, trong đó mỗi agent có một nhiệm vụ và chức năng riêng biệt, nhưng đều được điều phối bởi agent quản lý trung tâm. Điều này cho phép hệ thống xử lý nhiều loại yêu cầu khác nhau một cách linh hoạt và hiệu quả, đồng thời dễ dàng mở rộng và bảo trì trong tương lai.

Hệ thống Agent IUH-Ecommerce được xây dựng dựa trên mô hình Multi-Agent System (MAS) với các nguyên tắc thiết kế cốt lõi:

1. **Phân rã Chức năng (Functional Decomposition):**
   - Chia nhỏ các nhu cầu thành các nhóm chức năng riêng biệt
   - Mỗi nhóm chức năng được đảm nhiệm bởi một hoặc nhiều agent chuyên biệt

2. **Chuyên môn hóa Agent (Agent Specialization):**
   - Mỗi agent là "chuyên gia" trong lĩnh vực của mình
   - Tối ưu hóa hiệu suất và dễ dàng bảo trì, nâng cấp

3. **Phối hợp và Giao tiếp (Coordination & Communication):**
   - Cơ chế giao tiếp hiệu quả giữa các agent
   - Chia sẻ thông tin và yêu cầu hỗ trợ lẫn nhau

4. **Điều phối Trung tâm (Central Orchestration):**
   - Agent Điều phối (Orchestrator) quản lý luồng hội thoại
   - Phân tích ý định và định tuyến yêu cầu

5. **Kiến thức/Ngữ cảnh Chia sẻ (Shared Knowledge/Context):**
   - Lưu trữ và truy cập thông tin chung
   - Quản lý hồ sơ người dùng và lịch sử tương tác

## 2. CƠ CHẾ HOẠT ĐỘNG - HỆ SINH THÁI AGENT

### 2.1. Agent Quản Lý (Manager)

Agent quản lý là thành phần trung tâm của hệ thống, đóng vai trò là "bộ não" điều phối tất cả các hoạt động. Đây là một `ConversableAgent` từ thư viện `autogen`, được cấu hình với các khả năng sau:

#### 2.1.1. Cấu Hình và Khởi Tạo

```python
config_list = [
    {
        "model": "gemini-2.0-flash",
        "api_key": env.GEMINI_API_KEY,
        "api_type": "google"
    }
]

Manager = ConversableAgent(
    name="manager",
    system_message="""Bạn là một trợ lý AI thông minh làm việc cho một sàn thương mại điện tử IUH-Ecomerce
    Bạn sẽ nhận đầu vào câu hỏi của người dùng về sàn thương mại điện tử IUH-Ecomerce
    Nhiệm vụ của bạn là trả lời câu hỏi của người dùng một cách chính xác và đầy đủ nhất có thể
    Nếu bạn chưa đủ thông tin trả lời, bạn hãy sử dụng các trợ lý khác để tìm kiếm thông tin
    Hãy trả về mô tả truy vấn Qdrant dưới dạng JSON:"
        "agent": "ProductAgent" | "PoliciAgent" | "MySelf" | "TransactionAgent" | "OrchestratorAgent" | "UserProfileAgent" | "SearchDiscoveryAgent" | "RecommendationAgent" | "ProductInfoAgent" | "ReviewAgent" | "ProductComparisonAgent",
        "query": String
    Với Agent là tên của trợ lý mà bạn muốn sử dụng để tìm kiếm thông tin""",
    llm_config={"config_list": config_list},
    human_input_mode="NEVER"
)
```

#### 2.1.2. Cấu Trúc Yêu Cầu

```python
class ChatbotRequest(BaseModel):
    chat_id: int
    message: str
    context: dict = None
    user_id: Optional[int] = None
    shop_id: Optional[int] = None
    entities: Optional[Dict[str, Any]] = None
```

#### 2.1.3. Quy Trình Xử Lý

1. **Phân Tích Tin Nhắn**
```python
async def get_product_info(query):
    chat = await Manager.a_generate_reply(
        messages=[{"role": "user", "content": query}])
    
    # Extract JSON from the response content
    content = chat.get('content', '')
    try:
        # Find JSON in the content
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = content[json_start:json_end]
            response = json.loads(json_str)
        else:
            # If no JSON found, create a default response
            response = {
                "agent": "MySelf",
                "query": query
            }
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        # Fallback to default response
        response = {
            "agent": "MySelf",
            "query": query
        }
    return response
```

2. **Điều Phối Agent**
```python
async def call_agent(agent, request):
    try:
        if agent == "ProductAgent":
            result = await product_agent(request)
        elif agent == "PoliciAgent":
            result = policy_agent(request)
        elif agent == "MySelf":
            result = {
                "message": "Xin chào! Tôi là trợ lý AI của IUH-Ecomerce. Tôi có thể giúp gì cho bạn?",
                "type": "greeting"
            }
        elif agent == "TransactionAgent":
            result = await search(request.message)
        elif agent == "OrchestratorAgent":
            orchestrator = OrchestratorAgent()
            result = await orchestrator.process_request(request)
        elif agent == "UserProfileAgent":
            user_profile = UserProfileAgent()
            user_request = UserProfileRequest(
                chat_id=request.chat_id,
                user_id=request.user_id,
                message=request.message,
                entities=request.entities or {}
            )
            result = await user_profile.process_request(user_request)
        elif agent == "SearchDiscoveryAgent":
            search_agent = SearchDiscoveryAgent()
            result = await search_agent.process_search(request)
        elif agent == "RecommendationAgent":
            recommendation_agent = RecommendationAgent()
            result = await recommendation_agent.process_recommendation(request)
        elif agent == "ProductInfoAgent":
            product_info_agent = ProductInfoAgent()
            result = await product_info_agent.process_request(request)
        elif agent == "ReviewAgent":
            review_agent = ReviewAgent()
            result = await review_agent.process_request(request)
        elif agent == "ProductComparisonAgent":
            comparison_agent = ProductComparisonAgent()
            result = await comparison_agent.process_request(request)
        else:
            return {
                "message": "Xin lỗi, tôi không hiểu yêu cầu của bạn. Bạn có thể thử lại không?",
                "type": "error"
            }
        return result
    except Exception as e:
        logger.error(f"Error in call_agent: {str(e)}")
        return {
            "message": "Xin lỗi, đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
            "type": "error",
            "error": str(e)
        }
```

#### 2.1.4. Quản Lý Phiên Hội Thoại

1. **Tạo Phiên Mới**
```python
if request.chat_id == 0 or request.chat_id is None:
    new_chat = ChatCreate(
        shop_id=request.shop_id or 1,
        customer_id=request.user_id
    )
    chat = chat_service.create_session(new_chat)
    request.chat_id = chat.chat_id
```

2. **Lưu Trữ Tin Nhắn**
```python
message_payload = ChatMessageCreate(
    chat_id=request.chat_id,
    content=message,
    sender_type="customer",
    sender_id=request.user_id or 1
)
MessageRepository.create_message(message_payload)
```

3. **Lưu Trữ Phản Hồi**
```python
response_payload = ChatMessageCreate(
    chat_id=request.chat_id,
    content=result.get("message", str(result)),
    sender_type="shop",
    sender_id=request.shop_id if request.shop_id is not None else 1
)
MessageRepository.create_message(response_payload)
```

#### 2.1.5. Xử Lý Lỗi và Logging

1. **Logging**
```python
logger.error(f"Lỗi khi xử lý tin nhắn: {str(e)}")
logger.info(f"Đã tạo chat mới với ID: {chat.chat_id}")
```

2. **Xử Lý Lỗi**
```python
try:
    # Xử lý request
    result = await process_request(request)
    return result
except Exception as e:
    logger.error(f"Lỗi không xác định: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
```

#### 2.1.6. Các Agent Được Hỗ Trợ

1. **ProductAgent**: Tìm kiếm thông tin sản phẩm
2. **PoliciAgent**: Xử lý các truy vấn về chính sách
3. **MySelf**: Xử lý các câu hỏi thông thường
4. **TransactionAgent**: Xử lý các giao dịch
5. **OrchestratorAgent**: Điều phối xử lý NLU
6. **UserProfileAgent**: Quản lý thông tin người dùng
7. **SearchDiscoveryAgent**: Tìm kiếm và khám phá sản phẩm
8. **RecommendationAgent**: Đề xuất sản phẩm
9. **ProductInfoAgent**: Cung cấp thông tin chi tiết sản phẩm
10. **ReviewAgent**: Phân tích đánh giá
11. **ProductComparisonAgent**: So sánh sản phẩm

### 2.2. Các Agent Chuyên Biệt cho Khách Hàng

#### 2.2.1. ProductAgent (qdrant_agent.py)
- **Chức năng chính:** Xử lý các truy vấn liên quan đến thông tin sản phẩm
- **Khả năng chi tiết:**
  - Tìm kiếm sản phẩm dựa trên vector embedding
  - Phân tích ngữ nghĩa của truy vấn
  - Tích hợp với Qdrant vector database
  - Hỗ trợ tìm kiếm đa ngôn ngữ
- **Cấu trúc dữ liệu:**
  ```python
  {
      "collection_name": "products",
      "payload": "từ khóa tìm kiếm",
      "limit": 20,
      "function": "search | recommend_similar | recommend_for_user"
  }
  ```
- **Vai trò trong MAS:**
  - Xử lý các truy vấn về sản phẩm
  - Tích hợp với vector database
  - Cung cấp thông tin chi tiết
  - Hỗ trợ tìm kiếm thông minh

#### 2.2.2. PoliciAgent (polici_agent.py)
- **Chức năng chính:** Xử lý các truy vấn về chính sách và quy định
- **Khả năng chi tiết:**
  - Tìm kiếm thông tin chính sách
  - Phân tích ngữ nghĩa câu hỏi
  - Trích xuất thông tin liên quan
  - Cung cấp hướng dẫn chi tiết
- **Vai trò trong MAS:**
  - Cung cấp thông tin chính sách
  - Hỗ trợ giải đáp thắc mắc
  - Đảm bảo tuân thủ quy định
  - Cập nhật thông tin mới

#### 2.2.3. OrchestratorAgent (orchestrator_agent.py)
- **Chức năng chính:** Điều phối xử lý NLU và phân tích ý định
- **Khả năng chi tiết:**
  - Phân tích ý định người dùng
  - Trích xuất thực thể
  - Định tuyến yêu cầu
  - Quản lý ngữ cảnh hội thoại
- **Vai trò trong MAS:**
  - Điều phối xử lý ngôn ngữ
  - Phân tích ý định
  - Quản lý luồng hội thoại
  - Tối ưu hóa phản hồi

#### 2.2.4. UserProfileAgent (user_profile_agent.py)
- **Chức năng chính:** Quản lý thông tin và hành vi người dùng
- **Khả năng chi tiết:**
  - Xác thực người dùng
  - Quản lý profile
  - Phân tích hành vi
  - Tích hợp với hệ thống thành viên
- **Cấu trúc dữ liệu:**
  ```python
  class UserProfileRequest(BaseModel):
      chat_id: int
      user_id: int
      message: str
      entities: Dict[str, Any]
  ```
- **Vai trò trong MAS:**
  - Quản lý thông tin người dùng
  - Xác thực và phân quyền
  - Phân tích hành vi
  - Tích hợp OAuth

#### 2.2.5. SearchDiscoveryAgent (search_discovery_agent.py)
- **Chức năng chính:** Tìm kiếm và khám phá sản phẩm
- **Khả năng chi tiết:**
  - Tìm kiếm thông minh
  - Phân tích ngữ nghĩa
  - Tích hợp Elasticsearch
  - Hỗ trợ tìm kiếm nâng cao
- **Vai trò trong MAS:**
  - Hỗ trợ tìm kiếm sản phẩm
  - Phân tích ngữ nghĩa truy vấn
  - Tích hợp với Elasticsearch
  - Cải thiện trải nghiệm tìm kiếm

#### 2.2.6. RecommendationAgent (recommendation_agent.py)
- **Chức năng chính:** Đề xuất sản phẩm cá nhân hóa
- **Khả năng chi tiết:**
  - Phân tích hành vi người dùng
  - Xây dựng user profile
  - Tính toán độ tương đồng
  - Tạo danh sách đề xuất
- **Vai trò trong MAS:**
  - Đề xuất sản phẩm cá nhân hóa
  - Phân tích hành vi người dùng
  - Tích hợp machine learning
  - Cập nhật đề xuất real-time

#### 2.2.7. ProductInfoAgent (product_info_agent.py)
- **Chức năng chính:** Cung cấp thông tin chi tiết về sản phẩm
- **Khả năng chi tiết:**
  - Trích xuất thông tin sản phẩm
  - Tổng hợp thông tin từ nhiều nguồn
  - Phân tích đặc điểm sản phẩm
  - Cập nhật thông tin real-time
- **Vai trò trong MAS:**
  - Cung cấp thông tin chi tiết
  - Tổng hợp thông tin sản phẩm
  - Cập nhật thông tin real-time
  - Hỗ trợ quyết định mua hàng

#### 2.2.8. ReviewAgent (review_agent.py)
- **Chức năng chính:** Phân tích và tổng hợp đánh giá sản phẩm
- **Khả năng chi tiết:**
  - Phân tích cảm xúc (Sentiment Analysis)
  - Trích xuất thông tin quan trọng
  - Phân loại đánh giá
  - Tổng hợp thông tin
- **Vai trò trong MAS:**
  - Phân tích đánh giá sản phẩm
  - Tổng hợp thông tin từ reviews
  - Phát hiện spam và đánh giá giả
  - Cung cấp insights cho người dùng

#### 2.2.9. ProductComparisonAgent (product_comparison_agent.py)
- **Chức năng chính:** So sánh các sản phẩm tương tự
- **Khả năng chi tiết:**
  - Trích xuất thông số kỹ thuật
  - Tạo bảng so sánh trực quan
  - Làm nổi bật sự khác biệt
  - Đề xuất lựa chọn tối ưu
- **Vai trò trong MAS:**
  - Hỗ trợ quyết định mua hàng
  - Cải thiện trải nghiệm so sánh
  - Tích hợp với hệ thống sản phẩm
  - Phân tích xu hướng lựa chọn

#### 2.2.10. TransactionAgent (products.py, shopping_carts.py)
- **Chức năng chính:** Quản lý giao dịch và đơn hàng
- **Khả năng chi tiết:**
  - Xử lý đơn hàng
  - Quản lý giỏ hàng
  - Theo dõi thanh toán
  - Xử lý vận chuyển
- **Vai trò trong MAS:**
  - Quản lý giao dịch và đơn hàng
  - Tích hợp cổng thanh toán
  - Xử lý hoàn tiền và khiếu nại
  - Báo cáo giao dịch

### 2.3. Các Agent Chuyên Biệt cho Cửa Hàng

#### 2.3.1. ShopManagementAgent (shop_management_agent.py)
- **Chức năng chính:** Quản lý thông tin và hoạt động của cửa hàng
- **Khả năng chi tiết:**
  - Quản lý thông tin cửa hàng
  - Cập nhật trạng thái hoạt động
  - Xử lý yêu cầu từ khách hàng
  - Quản lý đánh giá và phản hồi
- **Vai trò trong MAS:**
  - Quản lý thông tin cửa hàng
  - Xử lý yêu cầu từ khách hàng
  - Cập nhật trạng thái hoạt động
  - Phân tích hiệu suất cửa hàng

#### 2.3.2. InventoryManagementAgent (inventory_management_agent.py)
- **Chức năng chính:** Quản lý tồn kho và nhập xuất hàng
- **Khả năng chi tiết:**
  - Theo dõi số lượng tồn kho
  - Cập nhật trạng thái sản phẩm
  - Quản lý nhập xuất hàng
  - Cảnh báo tồn kho thấp
- **Vai trò trong MAS:**
  - Quản lý tồn kho hiệu quả
  - Tối ưu hóa quy trình nhập xuất
  - Cảnh báo và thông báo
  - Phân tích xu hướng tồn kho

#### 2.3.3. OrderProcessingAgent (order_processing_agent.py)
- **Chức năng chính:** Xử lý và quản lý đơn hàng
- **Khả năng chi tiết:**
  - Xác nhận đơn hàng mới
  - Cập nhật trạng thái đơn hàng
  - Xử lý yêu cầu hủy/đổi trả
  - Tích hợp với đơn vị vận chuyển
- **Vai trò trong MAS:**
  - Tối ưu hóa quy trình xử lý đơn hàng
  - Cải thiện trải nghiệm khách hàng
  - Tích hợp với hệ thống vận chuyển
  - Phân tích hiệu suất xử lý đơn hàng

#### 2.3.4. AnalyticsAgent (analytics_agent.py)
- **Chức năng chính:** Phân tích và báo cáo hiệu suất kinh doanh
- **Khả năng chi tiết:**
  - Phân tích doanh số
  - Theo dõi sản phẩm bán chạy
  - Đánh giá hiệu quả marketing
  - Tạo báo cáo tự động
- **Vai trò trong MAS:**
  - Cung cấp insights kinh doanh
  - Hỗ trợ ra quyết định
  - Theo dõi hiệu suất
  - Phân tích xu hướng

#### 2.3.5. MarketingAgent (marketing_agent.py)
- **Chức năng chính:** Quản lý chiến dịch marketing và khuyến mãi
- **Khả năng chi tiết:**
  - Tạo và quản lý khuyến mãi
  - Phân tích hiệu quả chiến dịch
  - Đề xuất chiến lược marketing
  - Tích hợp với các kênh quảng cáo
- **Vai trò trong MAS:**
  - Tối ưu hóa chiến dịch marketing
  - Tăng hiệu quả khuyến mãi
  - Phân tích ROI
  - Cải thiện chiến lược marketing

#### 2.3.6. CustomerServiceAgent (customer_service_agent.py)
- **Chức năng chính:** Quản lý tương tác và hỗ trợ khách hàng
- **Khả năng chi tiết:**
  - Xử lý yêu cầu hỗ trợ
  - Quản lý khiếu nại
  - Tích hợp với hệ thống ticket
  - Phân tích phản hồi khách hàng
- **Vai trò trong MAS:**
  - Cải thiện chất lượng dịch vụ
  - Tăng sự hài lòng khách hàng
  - Tối ưu hóa quy trình hỗ trợ
  - Phân tích xu hướng khiếu nại

#### 2.3.7. FinanceAgent (finance_agent.py)
- **Chức năng chính:** Quản lý tài chính và thanh toán
- **Khả năng chi tiết:**
  - Theo dõi doanh thu
  - Quản lý chi phí
  - Xử lý thanh toán
  - Tạo báo cáo tài chính
- **Vai trò trong MAS:**
  - Quản lý tài chính hiệu quả
  - Tối ưu hóa chi phí
  - Đảm bảo minh bạch thanh toán
  - Phân tích hiệu suất tài chính

#### 2.3.8. PolicyComplianceAgent (policy_compliance_agent.py)
- **Chức năng chính:** Đảm bảo tuân thủ chính sách và quy định
- **Khả năng chi tiết:**
  - Kiểm tra tuân thủ chính sách
  - Cập nhật quy định mới
  - Xử lý vi phạm
  - Hướng dẫn tuân thủ
- **Vai trò trong MAS:**
  - Đảm bảo tuân thủ quy định
  - Giảm thiểu rủi ro
  - Cập nhật thông tin chính sách
  - Hỗ trợ tuân thủ

#### 2.3.9. ReviewManagementAgent (review_management_agent.py)
- **Chức năng chính:** Quản lý đánh giá và phản hồi từ khách hàng
- **Khả năng chi tiết:**
  - Theo dõi đánh giá mới
  - Phân tích cảm xúc đánh giá
  - Gợi ý phản hồi
  - Báo cáo thống kê
- **Vai trò trong MAS:**
  - Cải thiện chất lượng phản hồi
  - Tăng tương tác với khách hàng
  - Phân tích xu hướng đánh giá
  - Tối ưu hóa trải nghiệm khách hàng

#### 2.3.10. HumanHandoverAgent (human_handover_agent.py)
- **Chức năng chính:** Chuyển tiếp các vấn đề phức tạp cho nhân viên
- **Khả năng chi tiết:**
  - Nhận diện vấn đề phức tạp
  - Thu thập thông tin cần thiết
  - Chuyển tiếp đến bộ phận phù hợp
  - Theo dõi xử lý
- **Vai trò trong MAS:**
  - Đảm bảo xử lý vấn đề hiệu quả
  - Tối ưu hóa quy trình chuyển tiếp
  - Cải thiện trải nghiệm khách hàng
  - Phân tích hiệu suất xử lý

## 3. HƯỚNG DẪN SỬ DỤNG - TƯƠNG TÁC API

### 3.1. Tổng Quan về API

Hệ thống Agent IUH-Ecommerce cung cấp một tập hợp các API RESTful cho phép tương tác với các agent thông minh. Các API này được thiết kế để dễ dàng tích hợp vào các ứng dụng web, mobile và các hệ thống khác.

#### 3.1.1. Các Loại API
- **API Công khai:** Cho phép khách hàng và người dùng thông thường truy cập
- **API Nội bộ:** Dành cho các cửa hàng và quản trị viên
- **API Hệ thống:** Cho phép tích hợp với các hệ thống bên thứ ba

#### 3.1.2. Các Phương Thức HTTP Hỗ Trợ
- GET: Truy xuất thông tin
- POST: Tạo mới hoặc xử lý dữ liệu
- PUT: Cập nhật thông tin
- DELETE: Xóa thông tin

#### 3.1.3. Định Dạng Dữ Liệu
- Request/Response: JSON
- Encoding: UTF-8
- Content-Type: application/json

### 3.2. Endpoint Chính: `POST /manager/ask`

#### 3.2.1. Mục Đích
Endpoint này là điểm truy cập chính để tương tác với hệ thống agent, cho phép gửi tin nhắn và nhận phản hồi từ các agent thông minh.

#### 3.2.2. Cấu Trúc Yêu Cầu (`ChatbotRequest`)
```json
{
    "chat_id": int,            // ID của phiên trò chuyện hiện tại
    "message": "string",       // Truy vấn hoặc tin nhắn của người dùng
    "context": dict,           // Ngữ cảnh bổ sung cho truy vấn (tùy chọn)
    "user_id": int,            // ID của người dùng (tùy chọn)
    "shop_id": int,            // ID của cửa hàng (tùy chọn)
    "entities": dict           // Các thực thể được trích xuất (tùy chọn)
}
```

### 3.3. Quy Trình Xử Lý Chi Tiết

#### 3.3.1. Tiếp Nhận và Xác Thực Yêu Cầu
1. **Kiểm tra chat_id:**
   ```python
   if request.chat_id == 0 or request.chat_id is None:
       # Tạo chat mới với các giá trị mặc định
       new_chat = ChatCreate(
           shop_id=request.shop_id or 1,
           customer_id=request.user_id
       )
       chat = chat_service.create_session(new_chat)
       request.chat_id = chat.chat_id
   ```

2. **Lưu tin nhắn vào database:**
   ```python
   message_payload = ChatMessageCreate(
       chat_id=request.chat_id,
       content=message,
       sender_type="customer",
       sender_id=request.user_id or 1
   )
   MessageRepository.create_message(message_payload)
   ```

#### 3.3.2. Phân Tích và Xử Lý Yêu Cầu
1. **Phân tích tin nhắn:**
   ```python
   response = await get_product_info(message)
   agent = response.get("agent")
   query = response.get("query")
   ```

2. **Gọi agent phù hợp:**
   ```python
   result = await call_agent(agent, request)
   ```

3. **Lưu phản hồi:**
   ```python
   response_payload = ChatMessageCreate(
       chat_id=request.chat_id,
       content=result.get("message", str(result)),
       sender_type="shop",
       sender_id=request.shop_id if request.shop_id is not None else 1
   )
   MessageRepository.create_message(response_payload)
   ```

### 3.4. Các Agent Hỗ Trợ

#### 3.4.1. ProductAgent
- **Endpoint:** `/api/qdrant-agent`
- **Chức năng:** Tìm kiếm thông tin sản phẩm
- **Xử lý:** Tích hợp với Qdrant vector database

#### 3.4.2. PoliciAgent
- **Endpoint:** `/api/policies-agent`
- **Chức năng:** Xử lý các truy vấn về chính sách
- **Xử lý:** Tìm kiếm và trả về thông tin chính sách

#### 3.4.3. OrchestratorAgent
- **Endpoint:** `/api/orchestrator`
- **Chức năng:** Điều phối xử lý NLU
- **Xử lý:** Phân tích ý định và thực thể

#### 3.4.4. UserProfileAgent
- **Endpoint:** `/api/user-profile`
- **Chức năng:** Quản lý thông tin người dùng
- **Xử lý:** Xác thực và phân tích hành vi

#### 3.4.5. SearchDiscoveryAgent
- **Endpoint:** `/api/search-discovery`
- **Chức năng:** Tìm kiếm và khám phá sản phẩm
- **Xử lý:** Tích hợp với Elasticsearch

#### 3.4.6. RecommendationAgent
- **Endpoint:** `/api/recommendation`
- **Chức năng:** Đề xuất sản phẩm
- **Xử lý:** Phân tích và gợi ý sản phẩm

#### 3.4.7. ProductInfoAgent
- **Endpoint:** `/api/product-info`
- **Chức năng:** Cung cấp thông tin chi tiết sản phẩm
- **Xử lý:** Tổng hợp thông tin sản phẩm

#### 3.4.8. ReviewAgent
- **Endpoint:** `/api/reviews`
- **Chức năng:** Phân tích đánh giá
- **Xử lý:** Xử lý và tổng hợp đánh giá

#### 3.4.9. ProductComparisonAgent
- **Endpoint:** `/api/product-comparison`
- **Chức năng:** So sánh sản phẩm
- **Xử lý:** Phân tích và so sánh thông số

### 3.5. Xử Lý Lỗi

#### 3.5.1. Các Loại Lỗi
```python
try:
    # Xử lý request
    result = await process_request(request)
    return result
except Exception as e:
    logger.error(f"Lỗi không xác định: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
```

#### 3.5.2. Logging
```python
logger.error(f"Lỗi khi xử lý tin nhắn: {str(e)}")
logger.info(f"Đã tạo chat mới với ID: {chat.chat_id}")
```

### 3.6. Bảo Mật

#### 3.6.1. Xác Thực
- JWT Authentication
- API Key Management
- Session Management

#### 3.6.2. Kiểm Soát Truy Cập
- Role-based Access Control
- Rate Limiting
- Input Validation

### 3.7. Monitoring

#### 3.7.1. Health Check
- Endpoint: `/health`
- Status Monitoring
- System Health

#### 3.7.2. Logging
- Request Logging
- Error Tracking
- Performance Monitoring

### 3.8. Cấu Hình

#### 3.8.1. Model Configuration
```python
config_list = [
    {
        "model": "gemini-2.0-flash",
        "api_key": env.GEMINI_API_KEY,
        "api_type": "google"
    }
]
```

#### 3.8.2. System Message
```python
system_message = """Bạn là một trợ lý AI thông minh làm việc cho một sàn thương mại điện tử IUH-Ecommerce
Bạn sẽ nhận đầu vào câu hỏi của người dùng về sàn thương mại điện tử IUH-Ecommerce
Nhiệm vụ của bạn là trả lời câu hỏi của người dùng một cách chính xác và đầy đủ nhất có thể
Nếu bạn chưa đủ thông tin trả lời, bạn hãy sử dụng các trợ lý khác để tìm kiếm thông tin
Hãy trả về mô tả truy vấn Qdrant dưới dạng JSON:"
        "agent": "ProductAgent" | "PoliciAgent" | "MySelf" | "TransactionAgent" | "OrchestratorAgent" | "UserProfileAgent" | "SearchDiscoveryAgent" | "RecommendationAgent" | "ProductInfoAgent" | "ReviewAgent" | "ProductComparisonAgent",
        "query": String
    Với Agent là tên của trợ lý mà bạn muốn sử dụng để tìm kiếm thông tin""",
    llm_config={"config_list": config_list},
    human_input_mode="NEVER"
)
```

### 3.9. Tương Tác với Agent

#### 3.9.1. Gọi Agent
```python
async def call_agent(agent, request):
    try:
        if agent == "ProductAgent":
            result = await product_agent(request)
        elif agent == "PoliciAgent":
            result = policy_agent(request)
        elif agent == "MySelf":
            result = {
                "message": "Xin chào! Tôi là trợ lý AI của IUH-Ecomerce. Tôi có thể giúp gì cho bạn?",
                "type": "greeting"
            }
        elif agent == "TransactionAgent":
            result = await search(request.message)
        elif agent == "OrchestratorAgent":
            orchestrator = OrchestratorAgent()
            result = await orchestrator.process_request(request)
        elif agent == "UserProfileAgent":
            user_profile = UserProfileAgent()
            user_request = UserProfileRequest(
                chat_id=request.chat_id,
                user_id=request.user_id,
                message=request.message,
                entities=request.entities or {}
            )
            result = await user_profile.process_request(user_request)
        elif agent == "SearchDiscoveryAgent":
            search_agent = SearchDiscoveryAgent()
            result = await search_agent.process_search(request)
        elif agent == "RecommendationAgent":
            recommendation_agent = RecommendationAgent()
            result = await recommendation_agent.process_recommendation(request)
        elif agent == "ProductInfoAgent":
            product_info_agent = ProductInfoAgent()
            result = await product_info_agent.process_request(request)
        elif agent == "ReviewAgent":
            review_agent = ReviewAgent()
            result = await review_agent.process_request(request)
        elif agent == "ProductComparisonAgent":
            comparison_agent = ProductComparisonAgent()
            result = await comparison_agent.process_request(request)
        else:
            return {
                "message": "Xin lỗi, tôi không hiểu yêu cầu của bạn. Bạn có thể thử lại không?",
                "type": "error"
            }
        return result
    except Exception as e:
        logger.error(f"Error in call_agent: {str(e)}")
        return {
            "message": "Xin lỗi, đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
            "type": "error",
            "error": str(e)
        }
```

#### 3.9.2. Xử Lý Phản Hồi
```python
response = await get_product_info(message)
agent = response.get("agent")
query = response.get("query")

if agent and query:
    result = await call_agent(agent, request)
    return result
else:
    raise HTTPException(status_code=400, detail="Invalid response from manager")
```

Tài liệu này cung cấp tổng quan chi tiết về Hệ thống Agent IUH-Ecommerce. Để biết thêm thông tin về triển khai cụ thể của từng agent hoặc các điểm tích hợp khác, vui lòng tham khảo các module mã nguồn liên quan.
