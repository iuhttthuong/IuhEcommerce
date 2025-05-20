import json
from typing import Any, Dict, List, Optional, Union

import autogen
from autogen import ConversableAgent
from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel, Field

from env import env
from models.chats import ChatMessageCreate
from repositories.message import MessageRepository

router = APIRouter(prefix="/user-profile", tags=["User Profile"])

class UserProfileRequest(BaseModel):
    chat_id: int
    user_id: Optional[int] = None
    message: str
    entities: Optional[Dict[str, Any]] = None

class UserProfileResponse(BaseModel):
    content: str = Field(..., description="Nội dung phản hồi từ agent")
    user_data: Dict[str, Any] = Field(default_factory=dict, description="Dữ liệu người dùng")
    success: bool = Field(default=True, description="Trạng thái xử lý")
    
class UserProfileAction(BaseModel):
    action: str = Field(..., description="Hành động cần thực hiện: get_profile, update_profile, get_preferences, update_preferences")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tham số cho hành động")

class UserProfileAgent:
    def __init__(self):
        self.llm_config = {
            "model": "gpt-4o-mini",
            "api_key": env.OPENAI_API_KEY
        }
        self.agent = self._create_user_profile_agent()

    def _create_user_profile_agent(self) -> ConversableAgent:
        system_message = """
        Bạn là UserProfile Agent thông minh cho hệ thống hỗ trợ thương mại điện tử IUH-Ecommerce.
        
        Nhiệm vụ của bạn:
        1. Quản lý thông tin hồ sơ người dùng
        2. Cập nhật và lưu trữ thông tin người dùng (sở thích, lịch sử giao dịch, thông tin cá nhân)
        3. Cung cấp thông tin người dùng cho các agent khác khi cần
        4. Xác định thông tin nào nên được thu thập hoặc cập nhật
        
        Mỗi khi nhận được yêu cầu, bạn cần xác định:
        1. Thông tin nào người dùng đang chia sẻ
        2. Thông tin nào cần cập nhật
        3. Thông tin nào cần truy xuất
        
        Hãy trả về một JSON với cấu trúc:
        {
            "action": "get_profile | update_profile | get_preferences | update_preferences",
            "parameters": {
                "field_1": "value_1",
                "field_2": "value_2"
            },
            "explanation": "Mô tả ngắn gọn về hành động"
        }
        """
        return autogen.ConversableAgent(
            name="user_profile",
            system_message=system_message,
            llm_config=self.llm_config,
            human_input_mode="NEVER"
        )

    def _extract_action(self, response: str) -> Dict[str, Any]:
        try:
            # Tìm JSON trong kết quả
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                logger.warning(f"Không tìm thấy JSON trong phản hồi: {response}")
                return {"action": "error", "parameters": {}, "explanation": "Không thể phân tích phản hồi"}
        except json.JSONDecodeError as e:
            logger.error(f"Lỗi giải mã JSON: {e}")
            return {"action": "error", "parameters": {}, "explanation": f"Lỗi giải mã JSON: {e}"}

    async def _get_user_profile(self, user_id: int) -> Dict[str, Any]:
        # TODO: Implement integration with user database
        # Giả lập dữ liệu user cho mục đích demo
        return {
            "user_id": user_id,
            "name": "Nguyễn Văn A",
            "email": f"user{user_id}@example.com",
            "phone": "0123456789",
            "address": "123 Đường ABC, Quận XYZ, TP.HCM",
            "preferences": {
                "categories": ["electronics", "books"],
                "brands": ["Apple", "Samsung", "Dell"],
                "price_range": {"min": 100000, "max": 10000000}
            },
            "purchase_history": [
                {"order_id": 1001, "date": "2023-01-15", "total": 1500000},
                {"order_id": 1002, "date": "2023-02-20", "total": 2300000}
            ],
            "wishlist": [101, 203, 305],
            "loyalty_points": 150,
            "last_login": "2023-03-10T08:30:00Z"
        }

    async def _update_user_profile(self, user_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: Implement integration with user database to update profile
        # Giả lập cập nhật profile
        profile = await self._get_user_profile(user_id)
        
        # Cập nhật các trường cơ bản
        for key, value in updates.items():
            if key in profile and key != "user_id":
                profile[key] = value
                
        # Cập nhật preferences nếu có
        if "preferences" in updates and isinstance(updates["preferences"], dict):
            for pref_key, pref_value in updates["preferences"].items():
                profile["preferences"][pref_key] = pref_value
                
        return profile

    async def _get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        profile = await self._get_user_profile(user_id)
        return profile.get("preferences", {})

    async def _update_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> Dict[str, Any]:
        profile = await self._get_user_profile(user_id)
        
        # Cập nhật preferences
        for key, value in preferences.items():
            profile["preferences"][key] = value
            
        # TODO: Implement actual update to database
        
        return profile["preferences"]

    async def _execute_action(self, action: str, parameters: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        if action == "get_profile":
            return await self._get_user_profile(user_id)
        elif action == "update_profile":
            return await self._update_user_profile(user_id, parameters)
        elif action == "get_preferences":
            return await self._get_user_preferences(user_id)
        elif action == "update_preferences":
            return await self._update_user_preferences(user_id, parameters)
        else:
            logger.warning(f"Hành động không được hỗ trợ: {action}")
            return {"error": f"Hành động '{action}' không được hỗ trợ"}

    def _generate_response(self, action_result: Dict[str, Any], action: str) -> str:
        if action == "get_profile":
            return f"Thông tin hồ sơ của bạn: Tên: {action_result.get('name')}, Email: {action_result.get('email')}, SĐT: {action_result.get('phone')}"
        elif action == "update_profile":
            return "Hồ sơ của bạn đã được cập nhật thành công."
        elif action == "get_preferences":
            categories = ", ".join(action_result.get("categories", []))
            brands = ", ".join(action_result.get("brands", []))
            return f"Sở thích của bạn: Danh mục: {categories}, Thương hiệu: {brands}"
        elif action == "update_preferences":
            return "Sở thích của bạn đã được cập nhật thành công."
        else:
            return "Đã xảy ra lỗi khi xử lý yêu cầu của bạn."

    async def process_request(self, request: UserProfileRequest) -> UserProfileResponse:
        try:
            # Đảm bảo có user_id
            if not request.user_id:
                # Giả sử chat_id là user_id trong trường hợp này
                user_id = request.chat_id
            else:
                user_id = request.user_id
            
            # Phân tích yêu cầu
            prompt = f"""
            Hãy phân tích yêu cầu sau từ người dùng liên quan đến thông tin hồ sơ:
            "{request.message}"
            
            Các thực thể đã được xác định:
            {request.entities if request.entities else 'Không có thông tin thực thể.'}
            """
            
            # Gọi agent để phân tích
            agent_response = await self.agent.a_generate_reply(messages=[{"role": "user", "content": prompt}])
            
            # Trích xuất hành động
            action_info = self._extract_action(agent_response)
            action = action_info.get("action", "get_profile")
            parameters = action_info.get("parameters", {})
            
            # Thực hiện hành động
            action_result = await self._execute_action(action, parameters, user_id)
            
            # Tạo nội dung phản hồi
            response_content = self._generate_response(action_result, action)
            
            # Lưu thông tin tương tác vào message repository
            message_repository = MessageRepository()
            response_payload = ChatMessageCreate(
                chat_id=request.chat_id,
                role="assistant",
                content=response_content,
                metadata={"action": action, "result": "success"}
            )
            message_repository.create(response_payload)
            
            return UserProfileResponse(
                content=response_content,
                user_data=action_result,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Lỗi trong user_profile_agent: {e}")
            return UserProfileResponse(
                content="Đã xảy ra lỗi khi xử lý thông tin hồ sơ của bạn.",
                user_data={},
                success=False
            )
            
@router.post("/process", response_model=UserProfileResponse)
async def process_request(request: UserProfileRequest):
    try:
        agent = UserProfileAgent()
        response = await agent.process_request(request)
        return response
    except Exception as e:
        logger.error(f"Lỗi trong process_request endpoint: {e}")
        raise HTTPException(status_code=500, detail="Đã xảy ra lỗi khi xử lý yêu cầu.") 