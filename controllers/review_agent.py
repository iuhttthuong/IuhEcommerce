import json
from typing import Any, Dict, List, Optional, Union
from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from openai import OpenAI

from env import env
from db import get_db
from repositories.reviews import ReviewRepositories
from repositories.search import SearchRepository
from repositories.products import ProductRepositories

router = APIRouter(prefix="/reviews", tags=["Reviews"])

class ReviewRequest(BaseModel):
    chat_id: int
    message: str
    product_id: Optional[int] = None
    entities: Optional[Dict[str, Any]] = None

class ReviewResponse(BaseModel):
    content: str = Field(..., description="Nội dung phản hồi từ agent")
    product_id: Optional[int] = Field(default=None, description="ID sản phẩm")
    review_summary: Optional[Dict[str, Any]] = Field(default=None, description="Tóm tắt đánh giá")
    query_type: str = Field(..., description="Loại truy vấn: review, error")
    
class ReviewAgent:
    def __init__(self, db: Session):
        self.db = db
        self.review_repo = ReviewRepositories(db)
        self.product_repo = ProductRepositories(db)
        self.search_repo = SearchRepository()
        self.client = OpenAI(api_key=env.OPENAI_API_KEY)

    def find_product_by_name(self, product_name: str) -> Optional[int]:
        """Find product ID by name using semantic search."""
        try:
            search_results = self.search_repo.semantic_search(
                query=product_name,
                collection_name="product_embeddings",
                limit=1
            )
            
            if search_results and len(search_results) > 0:
                best_match = search_results[0]
                if best_match["score"] >= 0.7:
                    return best_match["payload"]["product_id"]
            
            product = self.db.query(Product).filter(
                Product.name.ilike(f"%{product_name}%")
            ).first()
            
            return product.id if product else None
        except Exception as e:
            logger.error(f"Error finding product by name: {str(e)}")
            return None

    def get_product_sentiment(self, product_id: int) -> dict:
        """Get sentiment analysis for a product."""
        reviews = self.review_repo.get_by_product(product_id)
        if not reviews:
            return {
                "average_rating": 0,
                "sentiment_score": 0,
                "total_reviews": 0,
                "message": "Chưa có đánh giá nào cho sản phẩm này"
            }

        total_reviews = len(reviews)
        average_rating = sum(review.rating for review in reviews) / total_reviews

        return {
            "average_rating": round(average_rating, 2),
            "sentiment_score": round(average_rating / 5, 2),
            "total_reviews": total_reviews,
            "message": "Phân tích hoàn tất"
        }

    async def process_request(self, request: Union[ReviewRequest, 'ChatbotRequest']) -> ReviewResponse:
        try:
            # Convert ChatbotRequest to ReviewRequest if needed
            if hasattr(request, 'entities'):
                product_id = None
                if request.entities and 'product_id' in request.entities:
                    try:
                        product_id = int(request.entities['product_id'])
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid product_id in entities: {request.entities.get('product_id')}")
                
                request = ReviewRequest(
                    chat_id=request.chat_id,
                    message=request.message,
                    product_id=product_id,
                    entities=request.entities
                )

            # Get product sentiment data if available
            sentiment_data = None
            if request.product_id:
                sentiment_data = self.get_product_sentiment(request.product_id)

            # Generate response using GPT
            prompt = f"""Bạn là chuyên gia phân tích đánh giá sản phẩm của sàn thương mại điện tử IUH-Ecommerce.
Hãy phân tích và tổng hợp các đánh giá thực tế từ người dùng để tư vấn cho khách hàng.

Câu hỏi của khách hàng: {request.message}

Thông tin đánh giá sản phẩm:
{json.dumps(sentiment_data, ensure_ascii=False) if sentiment_data else "Không có thông tin đánh giá"}

Yêu cầu:
1. Nếu có thông tin đánh giá (có điểm trung bình và số lượng đánh giá):
   - Mở đầu bằng lời chào và cảm ơn khách hàng
   - Dựa trên {sentiment_data.get('total_reviews', 0) if sentiment_data else 0} đánh giá thực tế từ người dùng, phân tích:
     * Những điểm được người dùng đánh giá cao nhất (dựa trên điểm trung bình {sentiment_data.get('average_rating', 0) if sentiment_data else 0}/5)
     * Những vấn đề hoặc điểm yếu được người dùng đề cập nhiều nhất
     * Cảm nhận chung của người dùng về sản phẩm
   - Tổng hợp các ý kiến phổ biến nhất về:
     * Chất lượng và độ bền
     * Giá cả và giá trị
     * Tính năng và hiệu quả
     * Độ an toàn và độ tin cậy
     * Trải nghiệm sử dụng
   - Đưa ra kết luận dựa trên số liệu thực tế:
     * Tỷ lệ người dùng hài lòng
     * Những điểm cần lưu ý khi sử dụng
     * Khuyến nghị dựa trên đánh giá của đa số người dùng
   - KHÔNG sử dụng định dạng markdown hoặc ký tự đặc biệt
   - KHÔNG đánh số các phần, thay vào đó sử dụng các từ nối tự nhiên
   - KHÔNG nói "không có thông tin đánh giá" nếu đã có dữ liệu
   - Đảm bảo câu trả lời hoàn chỉnh và có kết luận rõ ràng

2. Nếu không có thông tin đánh giá (không có điểm trung bình hoặc số lượng đánh giá = 0):
   - Hướng dẫn chi tiết cách tìm kiếm sản phẩm trên sàn
   - Liệt kê các tiêu chí quan trọng cần xem xét khi mua sản phẩm
   - Đề xuất cách đánh giá sản phẩm trước khi mua

3. Giữ giọng điệu chuyên nghiệp và thân thiện
4. KHÔNG sử dụng từ "None" trong phản hồi
5. KHÔNG lặp lại thông tin đánh giá ở cuối câu trả lời
"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Bạn là chuyên gia phân tích đánh giá sản phẩm của sàn thương mại điện tử IUH-Ecommerce. Hãy phân tích và tổng hợp các đánh giá thực tế từ người dùng để tư vấn cho khách hàng một cách chuyên nghiệp."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            content = response.choices[0].message.content
            
            # If no product_id but we have a product name in the response, try to find it
            if not request.product_id:
                # Extract product name from GPT response
                product_name_prompt = f"""Trích xuất tên sản phẩm từ câu hỏi sau. Chỉ trả về tên sản phẩm, không có text khác.
Câu hỏi: {request.message}"""
                
                product_name_response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Bạn là trợ lý trích xuất thông tin. Chỉ trả về tên sản phẩm, không có text khác."},
                        {"role": "user", "content": product_name_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=50
                )
                
                product_name = product_name_response.choices[0].message.content.strip()
                if product_name:
                    found_product_id = self.find_product_by_name(product_name)
                    if found_product_id:
                        request.product_id = found_product_id
                        sentiment_data = self.get_product_sentiment(found_product_id)
                        # Generate new response with product information
                        new_prompt = f"""Bạn là chuyên gia phân tích đánh giá sản phẩm của sàn thương mại điện tử IUH-Ecommerce.
Hãy phân tích và tổng hợp các đánh giá thực tế từ người dùng để tư vấn cho khách hàng.

Câu hỏi của khách hàng: {request.message}

Thông tin đánh giá sản phẩm:
{json.dumps(sentiment_data, ensure_ascii=False) if sentiment_data else "Không có thông tin đánh giá"}

Yêu cầu:
1. Mở đầu bằng lời chào và cảm ơn khách hàng
2. Dựa trên {sentiment_data.get('total_reviews', 0) if sentiment_data else 0} đánh giá thực tế từ người dùng, phân tích:
   - Những điểm được người dùng đánh giá cao nhất (dựa trên điểm trung bình {sentiment_data.get('average_rating', 0) if sentiment_data else 0}/5)
   - Những vấn đề hoặc điểm yếu được người dùng đề cập nhiều nhất
   - Cảm nhận chung của người dùng về sản phẩm
3. Tổng hợp các ý kiến phổ biến nhất về:
   - Chất lượng và độ bền
   - Giá cả và giá trị
   - Tính năng và hiệu quả
   - Độ an toàn và độ tin cậy
   - Trải nghiệm sử dụng
4. Đưa ra kết luận dựa trên số liệu thực tế:
   - Tỷ lệ người dùng hài lòng
   - Những điểm cần lưu ý khi sử dụng
   - Khuyến nghị dựa trên đánh giá của đa số người dùng
5. Giữ giọng điệu chuyên nghiệp và thân thiện
6. KHÔNG sử dụng định dạng markdown hoặc ký tự đặc biệt
7. KHÔNG đánh số các phần, thay vào đó sử dụng các từ nối tự nhiên
8. KHÔNG sử dụng từ "None" trong phản hồi
9. KHÔNG lặp lại thông tin đánh giá ở cuối câu trả lời
10. Đảm bảo câu trả lời hoàn chỉnh và có kết luận rõ ràng
"""

                        new_response = self.client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "Bạn là chuyên gia phân tích đánh giá sản phẩm của sàn thương mại điện tử IUH-Ecommerce. Hãy phân tích và tổng hợp các đánh giá thực tế từ người dùng để tư vấn cho khách hàng một cách chuyên nghiệp."},
                                {"role": "user", "content": new_prompt}
                            ],
                            temperature=0.7,
                            max_tokens=1000
                        )
                        content = new_response.choices[0].message.content

                return ReviewResponse(
                content=content,
                product_id=request.product_id,
                review_summary=sentiment_data,
                query_type="review"
                )

        except Exception as e:
            logger.error(f"Unexpected error in process_request: {str(e)}")
            return ReviewResponse(
                content=f"Đã xảy ra lỗi khi xử lý yêu cầu: {str(e)}",
                query_type="error"
            )

@router.get("/analyze/{product_id}")
def analyze_reviews(product_id: int, db: Session = Depends(get_db)):
    try:
        agent = ReviewAgent(db)
        return agent.get_product_sentiment(product_id)
    except Exception as e:
        logger.error(f"Error in analyze_reviews endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze", response_model=ReviewResponse)
async def analyze_reviews(request: ReviewRequest, db: Session = Depends(get_db)):
    try:
        agent = ReviewAgent(db)
        response = await agent.process_request(request)
        return response
    except Exception as e:
        logger.error(f"Lỗi trong analyze_reviews endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Đã xảy ra lỗi khi xử lý yêu cầu: {str(e)}") 