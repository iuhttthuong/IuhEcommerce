# TÀI LIỆU HỆ THỐNG AGENT IUH-ECOMMERCE

## 1. TỔNG QUAN

### 1.1. Giới Thiệu

Hệ thống Agent IUH-Ecommerce là một framework trợ lý thông minh được thiết kế nhằm nâng cao trải nghiệm người dùng trên nền tảng thương mại điện tử IUH-Ecommerce. Hệ thống này có khả năng xử lý các truy vấn của người dùng, hiểu được ý định của họ, và tận dụng một bộ các agent chuyên biệt để cung cấp phản hồi chính xác và toàn diện hoặc thực hiện các hành động phù hợp.

### 1.2. Mục Tiêu và Phạm Vi

#### 1.2.1. Mục Tiêu
- Tự động hóa quy trình hỗ trợ khách hàng
- Cung cấp trải nghiệm mua sắm thông minh
- Tối ưu hóa quy trình quản lý cửa hàng
- Nâng cao hiệu quả tương tác người dùng
- Giảm thiểu thời gian phản hồi
- Tăng tỷ lệ hài lòng của khách hàng

#### 1.2.2. Phạm Vi
- Hỗ trợ khách hàng 24/7
- Quản lý thông tin sản phẩm
- Xử lý đơn hàng và thanh toán
- Quản lý tồn kho và vận chuyển
- Phân tích và báo cáo kinh doanh
- Tích hợp với các hệ thống bên thứ ba

### 1.3. Kiến Trúc Tổng Thể

#### 1.3.1. Các Thành Phần Chính
1. **Frontend Layer**
   - Giao diện người dùng web
   - Ứng dụng di động
   - Dashboard quản trị
   - API Gateway

2. **Backend Layer**
   - FastAPI Framework
   - Database Systems
   - Message Queue
   - Cache System

3. **AI Layer**
   - Agent Management System
   - Natural Language Processing
   - Machine Learning Models
   - Vector Database

4. **Integration Layer**
   - Third-party APIs
   - Payment Gateways
   - Shipping Services
   - Analytics Tools

#### 1.3.2. Luồng Dữ Liệu
```
User Request → API Gateway → Agent Manager → Specialized Agents → Response
```

### 1.4. Công Nghệ Sử Dụng

#### 1.4.1. Core Technologies
- **Backend:** Python, FastAPI, SQLAlchemy
- **Database:** PostgreSQL, Redis, MongoDB
- **AI/ML:** AutoGen, Gemini 2.0, Qdrant
- **DevOps:** Docker, Kubernetes, CI/CD

#### 1.4.2. Các Thư Viện Chính
- **Web Framework:** FastAPI, Uvicorn
- **Database ORM:** SQLAlchemy, Alembic
- **AI Framework:** AutoGen, Transformers
- **Vector DB:** Qdrant, FAISS
- **Monitoring:** Prometheus, Grafana

### 1.5. Tính Năng Chính

#### 1.5.1. Cho Khách Hàng
- Tìm kiếm sản phẩm thông minh
- Gợi ý sản phẩm cá nhân hóa
- Hỗ trợ thanh toán và vận chuyển
- Theo dõi đơn hàng
- Đánh giá và phản hồi
- Hỗ trợ đổi trả

#### 1.5.2. Cho Cửa Hàng
- Quản lý sản phẩm và tồn kho
- Xử lý đơn hàng tự động
- Phân tích kinh doanh
- Quản lý khuyến mãi
- Hỗ trợ khách hàng
- Báo cáo và thống kê

### 1.6. Lợi Ích và Giá Trị

#### 1.6.1. Cho Khách Hàng
- Trải nghiệm mua sắm liền mạch
- Phản hồi nhanh chóng 24/7
- Thông tin chính xác và đầy đủ
- Hỗ trợ đa kênh
- Gợi ý sản phẩm phù hợp
- Quy trình đổi trả đơn giản

#### 1.6.2. Cho Cửa Hàng
- Tự động hóa quy trình
- Giảm chi phí vận hành
- Tăng hiệu suất xử lý
- Phân tích dữ liệu chi tiết
- Quản lý tồn kho hiệu quả
- Tối ưu hóa doanh số

### 1.7. Tương Thích và Tích Hợp

#### 1.7.1. Hệ Thống Tương Thích
- Web browsers (Chrome, Firefox, Safari)
- Mobile platforms (iOS, Android)
- Desktop applications
- Third-party integrations

#### 1.7.2. API Integration
- RESTful APIs
- WebSocket support
- OAuth 2.0 authentication
- Rate limiting
- Versioning

### 1.8. Bảo Mật và Tuân Thủ

#### 1.8.1. Bảo Mật
- Mã hóa dữ liệu
- Xác thực đa yếu tố
- Kiểm soát truy cập
- Bảo vệ API
- Audit logging

#### 1.8.2. Tuân Thủ
- GDPR compliance
- Data privacy
- Security standards
- Industry regulations
- Best practices

### 1.9. Khả Năng Mở Rộng

#### 1.9.1. Mở Rộng Theo Chiều Ngang
- Load balancing
- Auto-scaling
- Multi-region deployment
- High availability

#### 1.9.2. Mở Rộng Theo Chiều Dọc
- Performance optimization
- Resource scaling
- Database sharding
- Cache optimization

### 1.10. Kế Hoạch Phát Triển

#### 1.10.1. Giai Đoạn Hiện Tại
- Tối ưu hóa hiệu suất
- Cải thiện độ chính xác
- Mở rộng tính năng
- Tăng cường bảo mật

#### 1.10.2. Kế Hoạch Tương Lai
- AI/ML nâng cao
- Tích hợp đa nền tảng
- Mở rộng ngôn ngữ
- Tính năng mới

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

#### 2.1.1. Vai Trò và Trách Nhiệm

1. **Điều Phối Trung Tâm**
   - Phân tích và định tuyến yêu cầu
   - Quản lý luồng hội thoại
   - Điều phối các agent chuyên biệt
   - Đảm bảo tính nhất quán

2. **Xử Lý Ngôn Ngữ Tự Nhiên**
   - Phân tích ý định người dùng
   - Trích xuất thực thể
   - Hiểu ngữ cảnh hội thoại
   - Xác định độ ưu tiên

3. **Quản Lý Phiên**
   - Tạo và duy trì phiên hội thoại
   - Lưu trữ lịch sử tương tác
   - Quản lý trạng thái phiên
   - Xử lý timeout và retry

4. **Xử Lý Lỗi và Recovery**
   - Phát hiện và xử lý lỗi
   - Khôi phục từ lỗi
   - Chuyển tiếp đến agent phù hợp
   - Ghi log và báo cáo

#### 2.1.2. Cấu Trúc và Cấu Hình

1. **Cấu Hình Cơ Bản**
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
    system_message="""Bạn là một trợ lý AI thông minh làm việc cho một sàn thương mại điện tử IUH-Ecommerce...""",
    llm_config={"config_list": config_list},
    human_input_mode="NEVER"
)
```

2. **Các Tham Số Cấu Hình**
   - Model configuration
   - API endpoints
   - Timeout settings
   - Retry policies
   - Rate limiting
   - Cache settings

3. **Hệ Thống Prompt**
   - System message
   - Context management
   - Response formatting
   - Error handling

#### 2.1.3. Quy Trình Xử Lý

1. **Tiếp Nhận Yêu Cầu**
```python
async def ask_chatbot(request: ChatbotRequest):
    try:
        # Validate request
        # Create/retrieve chat session
        # Store message
        # Process request
        # Return response
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

2. **Phân Tích Yêu Cầu**
   - Xác định loại yêu cầu
   - Trích xuất thông tin
   - Phân loại độ ưu tiên
   - Chọn agent phù hợp

3. **Điều Phối Agent**
   - Gọi agent chuyên biệt
   - Xử lý phản hồi
   - Tổng hợp kết quả
   - Định dạng phản hồi

#### 2.1.4. Tích Hợp và Tương Tác

1. **Tích Hợp với Database**
   - Lưu trữ tin nhắn
   - Quản lý phiên
   - Theo dõi trạng thái
   - Phân tích dữ liệu

2. **Tương Tác với Agent Khác**
   - Gọi agent chuyên biệt
   - Chia sẻ ngữ cảnh
   - Xử lý phản hồi
   - Điều phối luồng

3. **Xử Lý Bất Đồng Bộ**
   - Async/await pattern
   - Concurrent processing
   - Timeout handling
   - Error recovery

#### 2.1.5. Bảo Mật và Kiểm Soát

1. **Xác Thực và Phân Quyền**
   - API key validation
   - User authentication
   - Role-based access
   - Session management

2. **Kiểm Soát Truy Cập**
   - Rate limiting
   - IP filtering
   - Request validation
   - Resource quotas

3. **Bảo Mật Dữ Liệu**
   - Data encryption
   - Secure storage
   - Privacy protection
   - Audit logging

#### 2.1.6. Monitoring và Logging

1. **Hệ Thống Logging**
```python
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "handlers": ["console", "file", "elasticsearch"]
}
```

2. **Metrics và Monitoring**
   - Request count
   - Response time
   - Error rate
   - Resource usage
   - Performance metrics

3. **Alerting và Reporting**
   - Error alerts
   - Performance alerts
   - Usage reports
   - Health checks

#### 2.1.7. Xử Lý Lỗi và Recovery

1. **Các Loại Lỗi**
   - Validation errors
   - Authentication errors
   - Processing errors
   - System errors

2. **Chiến Lược Recovery**
   - Retry mechanism
   - Fallback options
   - Error propagation
   - State recovery

3. **Error Handling Flow**
```python
try:
    # Process request
    result = await process_request(request)
    return result
except ValidationError as e:
    logger.error(f"Validation error: {str(e)}")
    raise HTTPException(status_code=400, detail=str(e))
except AuthenticationError as e:
    logger.error(f"Authentication error: {str(e)}")
    raise HTTPException(status_code=401, detail=str(e))
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
```

#### 2.1.8. Tối Ưu Hóa và Hiệu Suất

1. **Caching Strategy**
   - Response caching
   - Session caching
   - Query caching
   - Cache invalidation

2. **Performance Optimization**
   - Async processing
   - Batch operations
   - Resource pooling
   - Load balancing

3. **Resource Management**
   - Memory usage
   - CPU utilization
   - Network bandwidth
   - Database connections

#### 2.1.9. Testing và Quality Assurance

1. **Unit Testing**
   - Function testing
   - Integration testing
   - Performance testing
   - Security testing

2. **Monitoring và Validation**
   - Input validation
   - Output validation
   - State validation
   - Error validation

3. **Quality Metrics**
   - Response accuracy
   - Processing time
   - Error rate
   - User satisfaction

#### 2.1.10. Tài Liệu và Hướng Dẫn

1. **API Documentation**
   - Endpoint descriptions
   - Request/response formats
   - Error codes
   - Usage examples

2. **Development Guide**
   - Setup instructions
   - Configuration guide
   - Best practices
   - Troubleshooting

3. **Maintenance Guide**
   - Update procedures
   - Backup/restore
   - Monitoring
   - Performance tuning

### 2.2. Các Agent Chuyên Biệt cho Khách Hàng

#### 2.2.1. ProductAgent (qdrant_agent.py)
- **Chức năng chính:** Xử lý các truy vấn liên quan đến thông tin sản phẩm
- **Khả năng chi tiết:**
  - Tìm kiếm sản phẩm dựa trên vector embedding
  - Phân tích ngữ nghĩa của truy vấn
  - Tích hợp với Qdrant vector database
  - Hỗ trợ tìm kiếm đa ngôn ngữ
- **Các tính năng đặc biệt:**
  - Tìm kiếm theo vector similarity
  - Lọc kết quả theo nhiều tiêu chí
  - Xếp hạng kết quả theo độ liên quan
  - Cache kết quả tìm kiếm
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

#### 2.2.2. SearchDiscoveryAgent (search_discovery_agent.py)
- **Chức năng chính:** Hỗ trợ tìm kiếm và khám phá sản phẩm
- **Khả năng chi tiết:**
  - Tìm kiếm thông minh dựa trên từ khóa
  - Phân tích ngữ nghĩa truy vấn
  - Tích hợp với Elasticsearch
  - Hỗ trợ tìm kiếm nâng cao
- **Các tính năng đặc biệt:**
  - Tìm kiếm theo nhiều trường
  - Phân loại kết quả
  - Gợi ý từ khóa
  - Lọc và sắp xếp thông minh

- **Vai trò trong MAS:**
  - Hỗ trợ tìm kiếm và khám phá
  - Tích hợp với Elasticsearch
  - Phân tích ngữ nghĩa truy vấn
  - Gợi ý từ khóa thông minh

#### 2.2.3. RecommendationAgent (recommendation_agent.py)
- **Chức năng chính:** Đề xuất sản phẩm cá nhân hóa
- **Khả năng chi tiết:**
  - Phân tích hành vi người dùng
  - Xây dựng user profile
  - Tính toán độ tương đồng
  - Tạo danh sách đề xuất
- **Các tính năng đặc biệt:**
  - Collaborative filtering
  - Content-based filtering
  - Hybrid recommendation
  - Real-time updates

- **Vai trò trong MAS:**
  - Đề xuất sản phẩm cá nhân hóa
  - Phân tích hành vi người dùng
  - Tích hợp machine learning
  - Cập nhật đề xuất real-time

#### 2.2.4. ReviewAgent (review_agent.py)
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

#### 2.2.5. Agent Hỗ trợ Thanh toán (Checkout Assistant Agent)
- **Chức năng chính:** Hỗ trợ quy trình thanh toán
- **Khả năng chi tiết:**
  - Hướng dẫn từng bước thanh toán
  - Tự động điền thông tin đã lưu
  - Đề xuất phương thức vận chuyển/thanh toán tối ưu
  - Nhắc nhở áp dụng coupon
- **Vai trò trong MAS:**
  - Tối ưu hóa trải nghiệm thanh toán
  - Giảm thiểu tỷ lệ bỏ giỏ hàng
  - Tích hợp với hệ thống thanh toán
  - Đảm bảo an toàn giao dịch

#### 2.2.6. Agent Tối ưu Giỏ hàng (Cart Optimizer Agent)
- **Chức năng chính:** Tối ưu hóa giỏ hàng
- **Khả năng chi tiết:**
  - Đề xuất sản phẩm mua kèm
  - Gợi ý tạo combo để được giá tốt
  - Kiểm tra và áp dụng coupon
  - Tính toán chi phí vận chuyển
- **Vai trò trong MAS:**
  - Tăng giá trị đơn hàng
  - Cải thiện tỷ lệ chuyển đổi
  - Tích hợp với hệ thống khuyến mãi
  - Phân tích hành vi mua hàng

#### 2.2.7. Agent Theo dõi Đơn hàng (Order Tracking Agent)
- **Chức năng chính:** Theo dõi trạng thái đơn hàng
- **Khả năng chi tiết:**
  - Cập nhật trạng thái đơn hàng
  - Dự đoán thời gian giao hàng
  - Thông báo khi có sự chậm trễ
  - Cung cấp thông tin vận chuyển
- **Vai trò trong MAS:**
  - Tăng tính minh bạch
  - Cải thiện trải nghiệm khách hàng
  - Tích hợp với hệ thống vận chuyển
  - Xử lý khiếu nại liên quan đến giao hàng

#### 2.2.8. Agent Hỗ trợ Đổi trả (Returns Assistant Agent)
- **Chức năng chính:** Hỗ trợ quy trình đổi trả
- **Khả năng chi tiết:**
  - Hướng dẫn quy trình đổi trả
  - Tự động tạo yêu cầu đổi trả
  - Sắp xếp lấy hàng
  - Cập nhật trạng thái xử lý
- **Vai trò trong MAS:**
  - Đơn giản hóa quy trình đổi trả
  - Tăng sự hài lòng của khách hàng
  - Tích hợp với hệ thống CSKH
  - Theo dõi và báo cáo

#### 2.2.9. Agent Hỗ trợ Sản phẩm (Product Support Agent)
- **Chức năng chính:** Hỗ trợ kỹ thuật và hướng dẫn sử dụng
- **Khả năng chi tiết:**
  - Cung cấp tài liệu hướng dẫn
  - Giải đáp thắc mắc thường gặp
  - Kết nối với hỗ trợ chuyên sâu
  - Cập nhật thông tin sản phẩm
- **Vai trò trong MAS:**
  - Cải thiện trải nghiệm sau mua
  - Giảm tải cho bộ phận CSKH
  - Tích hợp với knowledge base
  - Phân tích vấn đề thường gặp

#### 2.2.10. Agent Nhắc nhở Đánh giá (Review Prompt Agent)
- **Chức năng chính:** Thu thập đánh giá từ khách hàng
- **Khả năng chi tiết:**
  - Gửi lời nhắc viết đánh giá
  - Gợi ý các khía cạnh cần đánh giá
  - Theo dõi tỷ lệ phản hồi
  - Phân tích chất lượng đánh giá
- **Vai trò trong MAS:**
  - Tăng số lượng đánh giá
  - Cải thiện chất lượng phản hồi
  - Tích hợp với hệ thống đánh giá
  - Phân tích xu hướng đánh giá

#### 2.2.11. Agent Kết nối Cộng đồng (Community Connector Agent)
- **Chức năng chính:** Kết nối người dùng trong cộng đồng
- **Khả năng chi tiết:**
  - Gợi ý nhóm và diễn đàn phù hợp
  - Kết nối người dùng có cùng sở thích
  - Đề xuất cuộc thảo luận liên quan
  - Quản lý tương tác cộng đồng
- **Vai trò trong MAS:**
  - Xây dựng cộng đồng người dùng
  - Tăng tương tác và gắn kết
  - Tích hợp với hệ thống social
  - Phân tích hành vi cộng đồng

#### 2.2.12. Agent Theo dõi Giá (Price Watch Agent)
- **Chức năng chính:** Theo dõi và thông báo biến động giá
- **Khả năng chi tiết:**
  - Theo dõi giá sản phẩm
  - Thông báo khi có giảm giá
  - So sánh giá giữa các sản phẩm
  - Đề xuất thời điểm mua tốt nhất
- **Vai trò trong MAS:**
  - Tăng cơ hội mua hàng
  - Cải thiện trải nghiệm mua sắm
  - Tích hợp với hệ thống giá
  - Phân tích xu hướng giá

#### 2.2.13. Agent Tìm kiếm Deal/Coupon (Deal/Coupon Finder Agent)
- **Chức năng chính:** Tìm kiếm và đề xuất mã giảm giá
- **Khả năng chi tiết:**
  - Tìm mã giảm giá phù hợp
  - Đề xuất voucher và khuyến mãi
  - Kiểm tra tính hợp lệ
  - Tính toán lợi ích tối đa
- **Vai trò trong MAS:**
  - Tăng giá trị mua hàng
  - Cải thiện trải nghiệm khách hàng
  - Tích hợp với hệ thống khuyến mãi
  - Phân tích hiệu quả coupon

#### 2.2.14. Agent Hỏi & Đáp Thông minh (Intelligent Q&A Agent)
- **Chức năng chính:** Trả lời câu hỏi về sản phẩm và dịch vụ
- **Khả năng chi tiết:**
  - Tìm kiếm câu trả lời từ nhiều nguồn
  - Phân tích ngữ nghĩa câu hỏi
  - Tổng hợp thông tin chính xác
  - Chuyển tiếp đến hỗ trợ khi cần
- **Vai trò trong MAS:**
  - Cung cấp thông tin chính xác
  - Giảm thời gian chờ đợi
  - Tích hợp với knowledge base
  - Cải thiện chất lượng phản hồi

#### 2.2.15. Agent So sánh Sản phẩm (Product Comparison Agent)
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

### 2.3. Các Agent Chuyên Biệt cho Cửa Hàng

#### 2.3.1. TransactionAgent (products.py, shopping_carts.py)
- **Chức năng chính:** Quản lý giao dịch và đơn hàng
- **Khả năng chi tiết:**
  - Xử lý đơn hàng
  - Quản lý giỏ hàng
  - Theo dõi thanh toán
  - Xử lý vận chuyển
- **Các tính năng đặc biệt:**
  - Tích hợp nhiều cổng thanh toán
  - Tự động cập nhật trạng thái
  - Xử lý hoàn tiền
  - Báo cáo giao dịch

- **Vai trò trong MAS:**
  - Quản lý giao dịch và đơn hàng
  - Tích hợp cổng thanh toán
  - Xử lý hoàn tiền và khiếu nại
  - Báo cáo giao dịch

#### 2.3.2. UserProfileAgent (user_profile_agent.py)
- **Chức năng chính:** Quản lý thông tin người dùng
- **Khả năng chi tiết:**
  - Xác thực người dùng
  - Quản lý profile
  - Phân tích hành vi
  - Tích hợp với hệ thống thành viên
- **Các tính năng đặc biệt:**
  - Bảo mật thông tin
  - Phân quyền truy cập
  - Tích hợp OAuth
  - Quản lý phiên đăng nhập

- **Vai trò trong MAS:**
  - Quản lý thông tin người dùng
  - Xác thực và phân quyền
  - Phân tích hành vi
  - Tích hợp OAuth

#### 2.3.3. PoliciAgent (polici_agent.py)
- **Chức năng chính:** Quản lý chính sách và quy định
- **Khả năng chi tiết:**
  - Quản lý FAQ
  - Cập nhật chính sách
  - Xử lý khiếu nại
  - Hướng dẫn tuân thủ
- **Các tính năng đặc biệt:**
  - Tự động cập nhật
  - Phân loại câu hỏi
  - Tích hợp với hệ thống pháp lý
  - Báo cáo vi phạm

- **Vai trò trong MAS:**
  - Quản lý chính sách và quy định
  - Cập nhật và thông báo thay đổi
  - Xử lý khiếu nại
  - Tích hợp hệ thống pháp lý

#### 2.3.4. Agent Quản lý Sản phẩm (Product Listing & Management Agent)
- **Chức năng chính:** Quản lý danh sách và thông tin sản phẩm
- **Khả năng chi tiết:**
  - Hỗ trợ đăng sản phẩm mới
  - Cập nhật thông tin sản phẩm
  - Kiểm tra trạng thái duyệt
  - Quản lý hiển thị sản phẩm
- **Vai trò trong MAS:**
  - Tối ưu hóa quy trình đăng sản phẩm
  - Đảm bảo chất lượng thông tin
  - Tích hợp với hệ thống quản lý sản phẩm
  - Phân tích hiệu suất sản phẩm

#### 2.3.5. Agent Quản lý Tồn kho (Inventory Management Agent)
- **Chức năng chính:** Quản lý và tối ưu hóa tồn kho
- **Khả năng chi tiết:**
  - Kiểm tra số lượng tồn kho
  - Cập nhật tồn kho hàng loạt
  - Cảnh báo tồn kho thấp
  - Gợi ý lượng nhập hàng
- **Vai trò trong MAS:**
  - Tối ưu hóa quản lý tồn kho
  - Giảm thiểu thất thoát
  - Tích hợp với hệ thống kho
  - Phân tích xu hướng tồn kho

#### 2.3.6. Agent Xử lý Đơn hàng (Order Processing Agent)
- **Chức năng chính:** Xử lý và quản lý đơn hàng
- **Khả năng chi tiết:**
  - Thông báo đơn hàng mới
  - Hiển thị chi tiết đơn hàng
  - Cập nhật trạng thái đơn hàng
  - Hỗ trợ in phiếu giao hàng
- **Vai trò trong MAS:**
  - Tối ưu hóa quy trình xử lý
  - Cải thiện hiệu suất giao hàng
  - Tích hợp với hệ thống đơn hàng
  - Phân tích hiệu suất xử lý

#### 2.3.7. Agent Quản lý Vận chuyển (Shipment Management Agent)
- **Chức năng chính:** Quản lý quy trình vận chuyển
- **Khả năng chi tiết:**
  - Đăng ký đơn vị vận chuyển
  - Theo dõi trạng thái vận chuyển
  - Xử lý sự cố vận chuyển
  - Tối ưu hóa chi phí vận chuyển
- **Vai trò trong MAS:**
  - Cải thiện trải nghiệm giao hàng
  - Giảm thiểu rủi ro vận chuyển
  - Tích hợp với đơn vị vận chuyển
  - Phân tích hiệu suất vận chuyển

#### 2.3.8. Agent Xử lý Đổi trả & Khiếu nại (Returns & Disputes Agent)
- **Chức năng chính:** Xử lý yêu cầu đổi trả và khiếu nại
- **Khả năng chi tiết:**
  - Thông báo yêu cầu đổi trả
  - Hướng dẫn quy trình xử lý
  - Cập nhật trạng thái xử lý
  - Phân tích nguyên nhân
- **Vai trò trong MAS:**
  - Tối ưu hóa quy trình đổi trả
  - Cải thiện sự hài lòng khách hàng
  - Tích hợp với hệ thống CSKH
  - Phân tích xu hướng khiếu nại

#### 2.3.9. Agent Quản lý Marketing & Khuyến mãi (Marketing & Promotion Agent)
- **Chức năng chính:** Quản lý chiến dịch marketing và khuyến mãi
- **Khả năng chi tiết:**
  - Tạo và quản lý chương trình khuyến mãi
  - Kiểm tra hiệu quả chiến dịch
  - Gợi ý chiến dịch phù hợp
  - Phân tích ROI
- **Vai trò trong MAS:**
  - Tối ưu hóa chiến dịch marketing
  - Tăng hiệu quả khuyến mãi
  - Tích hợp với hệ thống marketing
  - Phân tích hiệu suất chiến dịch

#### 2.3.10. Agent Phân tích & Báo cáo (Analytics & Reporting Agent)
- **Chức năng chính:** Phân tích và báo cáo hiệu suất kinh doanh
- **Khả năng chi tiết:**
  - Cung cấp báo cáo doanh số
  - Phân tích sản phẩm bán chạy
  - Theo dõi lượng truy cập
  - Đánh giá hiệu quả marketing
- **Vai trò trong MAS:**
  - Cung cấp insights kinh doanh
  - Hỗ trợ ra quyết định
  - Tích hợp với hệ thống báo cáo
  - Phân tích xu hướng kinh doanh

#### 2.3.11. Agent Tài chính & Thanh toán (Finance & Payout Agent)
- **Chức năng chính:** Quản lý tài chính và thanh toán
- **Khả năng chi tiết:**
  - Cung cấp thông tin chu kỳ thanh toán
  - Theo dõi số tiền thanh toán
  - Quản lý lịch sử thanh toán
  - Giải thích các loại phí
- **Vai trò trong MAS:**
  - Tối ưu hóa quản lý tài chính
  - Đảm bảo minh bạch thanh toán
  - Tích hợp với hệ thống tài chính
  - Phân tích hiệu suất tài chính

#### 2.3.12. Agent Chính sách & Hỗ trợ Sàn (Platform Policy & Support Agent)
- **Chức năng chính:** Quản lý chính sách và hỗ trợ từ sàn
- **Khả năng chi tiết:**
  - Trả lời câu hỏi về quy định
  - Hướng dẫn sử dụng tính năng
  - Cập nhật chính sách mới
  - Hỗ trợ tuân thủ quy định
- **Vai trò trong MAS:**
  - Đảm bảo tuân thủ chính sách
  - Cải thiện trải nghiệm người bán
  - Tích hợp với hệ thống hỗ trợ
  - Phân tích vấn đề thường gặp

#### 2.3.13. Agent Quản lý Tương tác Khách hàng (Customer Interaction Agent)
- **Chức năng chính:** Quản lý tương tác với khách hàng
- **Khả năng chi tiết:**
  - Thông báo tin nhắn mới
  - Hiển thị đánh giá mới
  - Gợi ý câu trả lời
  - Quản lý phản hồi
- **Vai trò trong MAS:**
  - Cải thiện tương tác khách hàng
  - Tăng hiệu quả phản hồi
  - Tích hợp với hệ thống chat
  - Phân tích hành vi khách hàng

#### 2.3.14. Agent Chuyển tiếp (Human Handover Agent)
- **Chức năng chính:** Chuyển tiếp các vấn đề phức tạp
- **Khả năng chi tiết:**
  - Nhận diện vấn đề phức tạp
  - Thu thập thông tin cần thiết
  - Chuyển tiếp đến bộ phận hỗ trợ
  - Theo dõi xử lý
- **Vai trò trong MAS:**
  - Đảm bảo xử lý vấn đề hiệu quả
  - Tối ưu hóa quy trình chuyển tiếp
  - Tích hợp với hệ thống ticketing
  - Phân tích hiệu suất xử lý

#### 2.3.15. Agent Quản lý Đánh giá & Phản hồi (Review & Feedback Management Agent)
- **Chức năng chính:** Quản lý đánh giá và phản hồi từ khách hàng
- **Khả năng chi tiết:**
  - Theo dõi đánh giá mới
  - Phân tích cảm xúc đánh giá
  - Gợi ý phản hồi phù hợp
  - Báo cáo thống kê đánh giá
- **Vai trò trong MAS:**
  - Cải thiện chất lượng phản hồi
  - Tăng tương tác với khách hàng
  - Tích hợp với hệ thống đánh giá
  - Phân tích xu hướng đánh giá

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
    "context": {               // Ngữ cảnh bổ sung cho truy vấn
        "user_type": "customer|shop",  // Loại người dùng
        "previous_messages": [],       // Lịch sử tin nhắn
        "session_data": {}            // Dữ liệu phiên
    },
    "user_id": int,            // ID của người dùng
    "shop_id": int,            // ID của cửa hàng
    "entities": {              // Các thực thể được trích xuất
        "product_ids": [],
        "category_ids": [],
        "keywords": []
    }
}
```

#### 3.2.3. Các Tham Số Bổ Sung
- **language**: Ngôn ngữ của tin nhắn (mặc định: "vi")
- **priority**: Độ ưu tiên xử lý (1-5)
- **timeout**: Thời gian chờ tối đa (ms)
- **callback_url**: URL để gửi phản hồi bất đồng bộ

### 3.3. Quy Trình Xử Lý Chi Tiết

#### 3.3.1. Tiếp Nhận Yêu Cầu
1. **Xác thực đầu vào:**
   - Kiểm tra định dạng JSON
   - Xác thực các trường bắt buộc
   - Kiểm tra độ dài tin nhắn
   - Xác thực quyền truy cập

2. **Xử lý phiên trò chuyện:**
   ```python
   if request.chat_id == 0 or request.chat_id is None:
       new_chat = ChatCreate(
           shop_id=request.shop_id or 1,
           customer_id=request.user_id
       )
       chat = chat_service.create_session(new_chat)
       request.chat_id = chat.chat_id
   ```

3. **Lưu trữ tin nhắn:**
   ```python
   message_payload = ChatMessageCreate(
       chat_id=request.chat_id,
       content=message,
       sender_type="customer",
       sender_id=request.user_id or 1
   )
   MessageRepository.create_message(message_payload)
   ```

#### 3.3.2. Phân Tích Yêu Cầu
1. **Phân tích ngữ nghĩa:**
   - Xác định ý định người dùng
   - Trích xuất thực thể
   - Phân loại yêu cầu

2. **Chọn agent phù hợp:**
   ```python
   response = await get_product_info(message)
   agent = response.get("agent")
   query = response.get("query")
   ```

3. **Xử lý ngữ cảnh:**
   - Tải lịch sử hội thoại
   - Cập nhật trạng thái phiên
   - Xác định ngữ cảnh hiện tại

#### 3.3.3. Xử Lý Bởi Agent
1. **Điều phối agent:**
   ```python
   result = await call_agent(agent, request)
   ```

2. **Xử lý phản hồi:**
   - Định dạng kết quả
   - Thêm thông tin bổ sung
   - Xử lý lỗi

3. **Lưu trữ phản hồi:**
   ```python
   response_payload = ChatMessageCreate(
       chat_id=request.chat_id,
       content=result.get("message", str(result)),
       sender_type="shop",
       sender_id=request.shop_id if request.shop_id is not None else 1
   )
   MessageRepository.create_message(response_payload)
   ```

### 3.4. Cấu Trúc Phản Hồi

#### 3.4.1. Phản Hồi Thành Công
```json
{
    "message": "Nội dung phản hồi",
    "type": "loại_phản_hồi",
    "data": {
        "entities": [],
        "suggestions": [],
        "metadata": {}
    },
    "success": true,
    "timestamp": "2024-03-21T10:30:00Z",
    "session_id": "uuid",
    "processing_time": 150
}
```

#### 3.4.2. Phản Hồi Lỗi
```json
{
    "message": "Thông báo lỗi",
    "type": "error",
    "error": {
        "code": "ERROR_CODE",
        "details": "Chi tiết lỗi",
        "suggestion": "Gợi ý khắc phục"
    },
    "success": false,
    "timestamp": "2024-03-21T10:30:00Z"
}
```

### 3.5. Xử Lý Lỗi và Mã Trạng Thái

#### 3.5.1. Mã Lỗi Thường Gặp
```json
{
    "400": {
        "code": "BAD_REQUEST",
        "message": "Yêu cầu không hợp lệ",
        "details": "Chi tiết lỗi validation"
    },
    "401": {
        "code": "UNAUTHORIZED",
        "message": "Không có quyền truy cập",
        "details": "Thiếu hoặc sai token xác thực"
    },
    "403": {
        "code": "FORBIDDEN",
        "message": "Truy cập bị cấm",
        "details": "Không đủ quyền thực hiện"
    },
    "404": {
        "code": "NOT_FOUND",
        "message": "Không tìm thấy tài nguyên",
        "details": "ID không tồn tại"
    },
    "429": {
        "code": "RATE_LIMIT",
        "message": "Vượt quá giới hạn request",
        "details": "Số request tối đa trong khoảng thời gian"
    },
    "500": {
        "code": "INTERNAL_ERROR",
        "message": "Lỗi máy chủ",
        "details": "Lỗi xử lý nội bộ"
    }
}
```

#### 3.5.2. Xử Lý Lỗi Chi Tiết
```python
try:
    # Xử lý request
    result = await process_request(request)
    return result
except ValidationError as e:
    logger.error(f"Lỗi validation: {str(e)}")
    raise HTTPException(status_code=400, detail=str(e))
except AuthenticationError as e:
    logger.error(f"Lỗi xác thực: {str(e)}")
    raise HTTPException(status_code=401, detail=str(e))
except PermissionError as e:
    logger.error(f"Lỗi quyền truy cập: {str(e)}")
    raise HTTPException(status_code=403, detail=str(e))
except NotFoundError as e:
    logger.error(f"Không tìm thấy: {str(e)}")
    raise HTTPException(status_code=404, detail=str(e))
except RateLimitError as e:
    logger.error(f"Vượt quá giới hạn: {str(e)}")
    raise HTTPException(status_code=429, detail=str(e))
except Exception as e:
    logger.error(f"Lỗi không xác định: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
```

### 3.6. Bảo Mật và Xác Thực

#### 3.6.1. Xác Thực API
- **API Key:** Sử dụng cho các ứng dụng bên thứ ba
- **JWT Token:** Cho người dùng đã đăng nhập
- **OAuth 2.0:** Cho các dịch vụ tích hợp

#### 3.6.2. Các Biện Pháp Bảo Mật
- Rate limiting
- CORS policy
- Input validation
- Data encryption
- Audit logging

### 3.7. Tối Ưu Hóa và Hiệu Suất

#### 3.7.1. Caching
- Response caching
- Session caching
- Query caching

#### 3.7.2. Rate Limiting
```python
RATE_LIMIT = {
    "default": "100/hour",
    "premium": "1000/hour",
    "enterprise": "unlimited"
}
```

#### 3.7.3. Timeout và Retry
```python
TIMEOUT_CONFIG = {
    "default": 30,  # seconds
    "long_running": 300,
    "retry_attempts": 3,
    "retry_delay": 1
}
```

### 3.8. Monitoring và Logging

#### 3.8.1. Metrics
- Request count
- Response time
- Error rate
- Resource usage

#### 3.8.2. Logging
```python
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "handlers": ["console", "file", "elasticsearch"]
}
```

### 3.9. Versioning và Backward Compatibility

#### 3.9.1. API Versioning
- URL-based: `/v1/manager/ask`
- Header-based: `X-API-Version: 1.0`
- Content-type: `application/vnd.iuhecommerce.v1+json`

#### 3.9.2. Deprecation Policy
- Thông báo trước 6 tháng
- Hỗ trợ phiên bản cũ trong 12 tháng
- Migration guide
- Breaking changes documentation

Tài liệu này cung cấp tổng quan chi tiết về Hệ thống Agent IUH-Ecommerce. Để biết thêm thông tin về triển khai cụ thể của từng agent hoặc các điểm tích hợp khác, vui lòng tham khảo các module mã nguồn liên quan.
