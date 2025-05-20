from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from db import Session, get_db
from models.shops import Shop
from loguru import logger
from autogen import AssistantAgent, ConversableAgent
from env import env

router = APIRouter(prefix="/shop/chat", tags=["Shop Chat"])

# Configure the LLM
config_list = [
    {
        "model": "gemini-2.0-flash",
        "api_key": env.GEMINI_API_KEY,
        "api_type": "google"
    }
]

class ChatRequest(BaseModel):
    message: str
    shop_id: Optional[int] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    shop_info: Optional[Dict[str, Any]] = None

# Create the Shop Assistant Agent
ShopAssistant = AssistantAgent(
    name="shop_assistant",
    system_message="""Bạn là một trợ lý AI thông minh làm việc cho một cửa hàng trên sàn thương mại điện tử IUH-Ecomerce.
    Nhiệm vụ của bạn là:
    1. Trả lời các câu hỏi về cửa hàng
    2. Cung cấp thông tin về sản phẩm
    3. Hỗ trợ khách hàng với các vấn đề về đơn hàng
    4. Giải thích các chính sách của cửa hàng
    5. Hỗ trợ marketing và bán hàng
    
    Hãy luôn lịch sự, chuyên nghiệp và hữu ích trong mọi tương tác.
    """,
    llm_config={"config_list": config_list}
)

@router.post("/ask", response_model=ChatResponse)
async def ask_shop_assistant(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        # Get shop information if shop_id is provided
        shop_info = None
        if request.shop_id:
            shop = db.query(Shop).filter(Shop.seller_id == request.shop_id).first()
            if shop:
                shop_info = {
                    "seller_id": shop.seller_id,
                    "name": shop.name,
                    "mail": shop.mail,
                    "phone": shop.phone
                }
        
        # Prepare context for the assistant
        context = request.context or {}
        if shop_info:
            context["shop_info"] = shop_info
        
        # Create the message for the assistant
        message = {
            "role": "user",
            "content": f"""
            Context: {context}
            User message: {request.message}
            """
        }
        
        # Get response from the assistant
        response = await ShopAssistant.a_generate_reply(messages=[message])
        
        return ChatResponse(
            response=response,
            shop_info=shop_info
        )
        
    except Exception as e:
        logger.error(f"Error in shop chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 