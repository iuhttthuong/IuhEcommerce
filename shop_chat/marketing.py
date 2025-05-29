from fastapi import APIRouter, HTTPException
from autogen import AssistantAgent
from loguru import logger
from .base import BaseShopAgent, ShopRequest, ChatMessageRequest
from repositories.message import MessageRepository
from repositories.marketing import MarketingRepository
from models.coupons import Coupon, CouponCreate, CouponUpdate
from models.chats import ChatMessageCreate
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from services.search import SearchServices
import traceback
from decimal import Decimal
import re

router = APIRouter(prefix="/shop/marketing", tags=["Shop Marketing"])

class MarketingAgent(BaseShopAgent):
    def __init__(self, shop_id: int = None):
        super().__init__(
            shop_id=shop_id,
            name="MarketingAgent",
            system_message="""Bạn là một trợ lý AI chuyên nghiệp làm việc cho sàn thương mại điện tử IUH-Ecommerce, chuyên tư vấn và hướng dẫn cho người bán về marketing.

Nhiệm vụ của bạn:
1. Tư vấn chiến lược marketing
2. Hướng dẫn tạo chiến dịch
3. Tư vấn tối ưu quảng cáo
4. Đề xuất cải thiện hiệu quả

Các chức năng chính:
1. Chiến lược marketing:
   - Phân tích thị trường
   - Xác định mục tiêu
   - Lập kế hoạch
   - Đo lường hiệu quả
   - Điều chỉnh chiến lược

2. Tạo chiến dịch:
   - Thiết kế chiến dịch
   - Lập ngân sách
   - Chọn kênh quảng cáo
   - Tạo nội dung
   - Theo dõi kết quả

3. Tối ưu quảng cáo:
   - Phân tích hiệu quả
   - Điều chỉnh ngân sách
   - Tối ưu nội dung
   - Cải thiện targeting
   - Tăng ROI

4. Cải thiện hiệu quả:
   - Phân tích dữ liệu
   - Đề xuất cải thiện
   - Tối ưu chi phí
   - Tăng chuyển đổi
   - Nâng cao hiệu quả

Khi trả lời, bạn cần:
- Tập trung vào lợi ích của người bán
- Cung cấp hướng dẫn chi tiết
- Đề xuất giải pháp tối ưu
- Sử dụng ngôn ngữ chuyên nghiệp
- Cung cấp ví dụ cụ thể
- Nhấn mạnh các điểm quan trọng
- Hướng dẫn từng bước khi cần"""
        )
        self.message_repository = MessageRepository()
        self.collection_name = "marketing_embeddings"
        self.agent_name = "MarketingAgent"

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a marketing request."""
        try:
            print(f"requet 🤷‍♂️��‍♂️🙌🙌🙌🙌🙌🙌🙌🙌🙌{request}")
            print(request)
            message = request.message
            shop_id = request.shop_id
            # chat_history = request.['chat_history']
            chat_history = ""

            if not shop_id:
                return {
                    "message": "Không tìm thấy thông tin shop.",
                    "type": "error"
                }

            # Tạo prompt cho LLM
            prompt = self._build_prompt(message, f"Shop ID: {shop_id}\nChat History:\n{chat_history}")

            # Tạo response sử dụng assistant
            response = await self.assistant.a_generate_reply(
                messages=[{"role": "user", "content": prompt}]
            )

            return {
                "message": response if response else self._get_fallback_response(),
                "type": "text"
            }

        except Exception as e:
            logger.error(f"Error in MarketingAgent.process: {str(e)}")
            return {
                "message": self._get_fallback_response(),
                "type": "error"
            }

    def _build_prompt(self, query: str, context: str) -> str:
        return (
            f"Người bán hỏi: {query}\n"
            f"Thông tin marketing liên quan:\n{context}\n"
            "Hãy trả lời theo cấu trúc sau:\n"
            "1. Tóm tắt vấn đề:\n"
            "   - Mục đích và phạm vi\n"
            "   - Đối tượng áp dụng\n"
            "   - Tầm quan trọng\n\n"
            "2. Hướng dẫn chi tiết:\n"
            "   - Các bước thực hiện\n"
            "   - Yêu cầu cần thiết\n"
            "   - Lưu ý quan trọng\n\n"
            "3. Quy trình xử lý:\n"
            "   - Các bước thực hiện\n"
            "   - Thời gian xử lý\n"
            "   - Tài liệu cần thiết\n\n"
            "4. Tối ưu và cải thiện:\n"
            "   - Cách tối ưu\n"
            "   - Cải thiện hiệu quả\n"
            "   - Tăng trải nghiệm\n\n"
            "5. Khuyến nghị:\n"
            "   - Giải pháp tối ưu\n"
            "   - Cải thiện quy trình\n"
            "   - Tăng hiệu quả\n\n"
            "Trả lời cần:\n"
            "- Chuyên nghiệp và dễ hiểu\n"
            "- Tập trung vào lợi ích của người bán\n"
            "- Cung cấp hướng dẫn chi tiết\n"
            "- Đề xuất giải pháp tối ưu\n"
            "- Cung cấp ví dụ cụ thể"
        )

    def _get_response_title(self, query: str) -> str:
        return f"Marketing - {query.split()[0] if query else 'Hỗ trợ'}"

    def _get_fallback_response(self) -> str:
        return "Xin lỗi, tôi không thể tìm thấy thông tin chi tiết về vấn đề này. Vui lòng liên hệ bộ phận hỗ trợ shop để được tư vấn cụ thể hơn."

class Marketing:
    def __init__(self, db: Session, shop_id: int = None):
        self.db = db
        self.shop_id = shop_id
        self.agent = MarketingAgent(shop_id)
        self.marketing_repository = MarketingRepository(db)

    def _format_currency(self, value: Optional[Decimal]) -> str:
        """Format currency value with proper formatting"""
        if value is None:
            return "N/A"
        return f"{float(value):,.0f}đ"

    def _format_percentage(self, value: Optional[Decimal]) -> str:
        """Format percentage value with proper formatting"""
        if value is None:
            return "N/A"
        return f"{float(value)}%"

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a marketing request"""
        try:
            message = request.get('message', '').lower()
            context = request.get('context', {})
            intent = request.get('intent', '')
            # Tự động trích xuất thông tin từ message và merge vào context
            for k, v in extract_campaign_info_from_message(message).items():
                if v and not context.get(k):
                    context[k] = v

            # Nới lỏng điều kiện tạo coupon: nếu có campaign_goal, budget, duration thì tạo coupon, các trường còn lại điền mặc định
            defaults = {
                'channels': 'Facebook, Google',
                'target_audience': 'Tất cả khách hàng'
            }
            for k, v in defaults.items():
                if not context.get(k):
                    context[k] = v
            if context.get('campaign_goal') and context.get('budget') and context.get('duration'):
                from models.coupons import CouponCreate
                try:
                    coupon_data = CouponCreate(
                        code=context.get('code', f"SALE{datetime.now().strftime('%Y%m%d%H%M%S')}")[:20],
                        description=context.get('campaign_goal', ''),
                        discount_type=context.get('discount_type', 'percent'),
                        discount_value=float(context.get('discount_value', 10)),
                        min_purchase=float(context.get('min_purchase', 0)),
                        max_discount=float(context.get('max_discount', 0)),
                        start_date=context.get('start_date', datetime.now()),
                        end_date=context.get('end_date', datetime.now()),
                        is_active=True,
                        usage_limit=int(context.get('usage_limit', 100)),
                    )
                    coupon = self.marketing_repository.create(coupon_data)
                    return {
                        "message": f"Đã tạo chiến lược/chiến dịch thành công với mã: {coupon.code}",
                        "type": "success",
                        "data": {"coupon_id": coupon.coupon_id}
                    }
                except Exception as e:
                    logger.error(f"Error creating campaign coupon: {str(e)}")
                    return {
                        "message": "Không thể tạo chiến lược/chiến dịch. Vui lòng thử lại sau.",
                        "type": "error"
                    }

            # Lấy thông tin chiến dịch marketing
            campaigns = self.marketing_repository.get_active_campaigns()
            if not campaigns:
                return {
                    "message": "Chưa có chiến dịch marketing nào.",
                    "type": "text",
                    "data": {
                        "total_campaigns": 0,
                        "campaigns": []
                    }
                }

            # Format thông tin chiến dịch
            campaigns_info = []
            for campaign in campaigns:
                campaign_info = {
                    "campaign_id": campaign.coupon_id,
                    "name": campaign.code,
                    "description": campaign.description,
                    "start_date": campaign.start_date.isoformat() if campaign.start_date else None,
                    "end_date": campaign.end_date.isoformat() if campaign.end_date else None,
                    "discount_type": campaign.discount_type,
                    "discount_value": float(campaign.discount_value),
                    "min_purchase": float(campaign.min_purchase) if campaign.min_purchase else None,
                    "max_discount": float(campaign.max_discount) if campaign.max_discount else None,
                    "usage_limit": campaign.usage_limit,
                    "usage_count": campaign.usage_count,
                    "status": "active" if campaign.is_active else "inactive"
                }
                campaigns_info.append(campaign_info)

            # Tạo response
            response = {
                "message": f"Thông tin chiến dịch marketing:\n" + "\n".join([
                    f"- Chiến dịch: {campaign['name']}\n"
                    f"  + Loại giảm giá: {campaign['discount_type']}\n"
                    f"  + Giá trị giảm: {self._format_percentage(campaign['discount_value'])}\n"
                    f"  + Đơn hàng tối thiểu: {self._format_currency(campaign['min_purchase'])}\n"
                    f"  + Giảm tối đa: {self._format_currency(campaign['max_discount'])}\n"
                    f"  + Ngày bắt đầu: {campaign['start_date']}\n"
                    f"  + Ngày kết thúc: {campaign['end_date']}\n"
                    f"  + Trạng thái: {campaign['status']}"
                    for campaign in campaigns_info
                ]),
                "type": "text",
                "data": {
                    "total_campaigns": len(campaigns_info),
                    "campaigns": campaigns_info
                }
            }

            # Thêm thông tin chi tiết nếu có yêu cầu cụ thể
            if 'chi tiết' in message or 'detail' in message:
                response['message'] += "\n\nChi tiết chiến dịch:\n" + "\n".join([
                    f"- Chiến dịch: {campaign['name']}\n"
                    f"  + ID: {campaign['campaign_id']}\n"
                    f"  + Mô tả: {campaign['description']}\n"
                    f"  + Loại giảm giá: {campaign['discount_type']}\n"
                    f"  + Giá trị giảm: {self._format_percentage(campaign['discount_value'])}\n"
                    f"  + Đơn hàng tối thiểu: {self._format_currency(campaign['min_purchase'])}\n"
                    f"  + Giảm tối đa: {self._format_currency(campaign['max_discount'])}\n"
                    f"  + Ngày bắt đầu: {campaign['start_date']}\n"
                    f"  + Ngày kết thúc: {campaign['end_date']}\n"
                    f"  + Giới hạn sử dụng: {campaign['usage_limit']}\n"
                    f"  + Đã sử dụng: {campaign['usage_count']}\n"
                    f"  + Trạng thái: {campaign['status']}"
                    for campaign in campaigns_info
                ])

            return response

        except Exception as e:
            logger.error(f"Error processing marketing request: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "message": "Đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
                "type": "error",
                "error": str(e)
            }

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Alias for process method to maintain backward compatibility"""
        return await self.process(request)

@router.post("/query")
async def query_marketing(request: ChatMessageRequest):
    try:
        marketing = Marketing(Session())
        # Convert to ShopRequest format
        shop_request = ShopRequest(
            message=request.content,
            chat_id=request.chat_id,
            shop_id=request.sender_id if request.sender_type == "shop" else None,
            user_id=request.sender_id if request.sender_type == "user" else None,
            context=request.message_metadata if request.message_metadata else {},
            entities={},
            agent_messages=[],
            filters={}
        )
        response = await marketing.process(shop_request.dict())
        return response
    except Exception as e:
        logger.error(f"Error in query_marketing: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_campaigns():
    """List all marketing campaigns in a shop"""
    return {"message": "List campaigns endpoint"}

def extract_campaign_info_from_message(message: str) -> dict:
    info = {}
    # Mục tiêu/chiến dịch
    match_goal = re.search(r'(sale|khuyến mãi|chiến lược|chiến dịch|promotion|campaign)[^\n]*', message, re.IGNORECASE)
    if match_goal:
        info['campaign_goal'] = match_goal.group(0).strip()
    # Ngân sách
    match_budget = re.search(r'(\d+\s*(tr|triệu|million|m))', message, re.IGNORECASE)
    if match_budget:
        info['budget'] = match_budget.group(0).strip()
    # Kênh quảng bá
    match_channels = re.search(r'(facebook|google|email|zalo|tiktok|instagram)', message, re.IGNORECASE)
    if match_channels:
        info['channels'] = match_channels.group(0).strip()
    # Thời gian
    match_duration = re.search(r'(từ\s*\d{1,2}/\d{1,2}(-|đến|–)\d{1,2}/\d{1,2})', message, re.IGNORECASE)
    if match_duration:
        info['duration'] = match_duration.group(0).strip()
    # Đối tượng
    match_target = re.search(r'(tất cả khách hàng|khách hàng|everyone|all customers)', message, re.IGNORECASE)
    if match_target:
        info['target_audience'] = match_target.group(0).strip()
    return info
