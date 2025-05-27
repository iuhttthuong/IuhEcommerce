import json
from typing import Any, Dict, List, Optional, Union

import autogen
from autogen import ConversableAgent
from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from env import env
from models.chats import ChatMessageCreate
from models.customers import Customer, CustomerModel
from repositories.message import MessageRepository
from repositories.customers import CustomerRepository

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
    def __init__(self, db: Session):
        if not db:
            raise HTTPException(status_code=500, detail="Database connection is required")
            
        self.llm_config = {
            "model": "gpt-4o-mini",
            "api_key": env.OPENAI_API_KEY
        }
        self.agent = self._create_user_profile_agent()
        self.db = db

    def _create_user_profile_agent(self) -> ConversableAgent:
        system_message = """
        Bạn là UserProfile Agent thông minh cho hệ thống hỗ trợ thương mại điện tử IUH-Ecommerce.
        
        Nhiệm vụ của bạn:
        1. Quản lý thông tin hồ sơ người dùng
        2. Cập nhật và lưu trữ thông tin người dùng (sở thích, lịch sử giao dịch, thông tin cá nhân)
        3. Cung cấp thông tin người dùng cho các agent khác khi cần
        4. Xác định thông tin nào nên được thu thập hoặc cập nhật
        
        Khi người dùng yêu cầu thay đổi thông tin, bạn cần:
        1. Hỏi người dùng muốn thay đổi thông tin nào
        2. Yêu cầu người dùng cung cấp thông tin mới
        3. Xác nhận thông tin trước khi cập nhật
        
        Hãy trả về một JSON với cấu trúc:
        {
            "action": "get_profile | update_profile | get_preferences | update_preferences",
            "parameters": {
                "field": "tên trường cần thay đổi",
                "new_value": "giá trị mới",
                "needs_confirmation": true
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
                # Nếu không tìm thấy JSON, trả về action mặc định
                return {
                    "action": "get_profile",
                    "parameters": {},
                    "explanation": "Lấy thông tin hồ sơ người dùng"
                }
        except json.JSONDecodeError as e:
            logger.error(f"Lỗi giải mã JSON: {e}")
            return {
                "action": "get_profile",
                "parameters": {},
                "explanation": "Lấy thông tin hồ sơ người dùng"
            }

    async def _get_user_profile(self, user_id: int) -> Dict[str, Any]:
        if not self.db:
            raise HTTPException(status_code=500, detail="Database connection not initialized")
            
        customer = CustomerRepository.get_by_id(user_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
            
        return {
            "user_id": customer.customer_id,
            "name": f"{customer.customer_fname} {customer.customer_lname}",
            "email": customer.customer_mail,
            "phone": customer.customer_phone,
            "address": customer.customer_address,
            "dob": customer.customer_dob,
            "gender": customer.customer_gender,
            "preferences": {
                "categories": [],  # To be implemented
                "brands": [],      # To be implemented
                "price_range": {"min": 0, "max": 0}  # To be implemented
            }
        }

    async def _update_user_profile(self, user_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        if not self.db:
            raise HTTPException(status_code=500, detail="Database connection not initialized")
            
        # Lấy thông tin hiện tại của người dùng
        current_profile = await self._get_user_profile(user_id)
        
        # Tạo câu lệnh SQL và thực hiện cập nhật
        try:
            # Map các trường từ parameters sang tên cột trong database
            field_mapping = {
                "name": ("customer_fname", "customer_lname"),
                "email": "customer_mail",
                "phone": "customer_phone",
                "address": "customer_address",
                "dob": "customer_dob",
                "gender": "customer_gender"
            }

            update_data = {}
            if "field" in updates and "new_value" in updates:
                field = updates["field"]
                new_value = updates["new_value"]
                
                if field in field_mapping:
                    if field == "name":
                        # Xử lý tên riêng biệt
                        names = new_value.split()
                        if len(names) >= 2:
                            update_data["customer_fname"] = names[0]
                            update_data["customer_lname"] = " ".join(names[1:])
                    else:
                        # Các trường khác
                        db_field = field_mapping[field]
                        update_data[db_field] = new_value

            if update_data:
                # Tạo câu lệnh SQL
                set_clauses = [f"{k} = :{k}" for k in update_data.keys()]
                sql = f"""
                UPDATE customers 
                SET {', '.join(set_clauses)}
                WHERE customer_id = :customer_id
                """
                
                # Thực hiện cập nhật
                with self.db as session:
                    session.execute(sql, {**update_data, "customer_id": user_id})
                    session.commit()
                
                # Lấy thông tin mới sau khi cập nhật
                return await self._get_user_profile(user_id)
            else:
                raise HTTPException(status_code=400, detail="Không có thông tin nào được cập nhật")
                
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật thông tin người dùng: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật thông tin: {str(e)}")

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
            if not action_result:
                return "Không tìm thấy thông tin hồ sơ của bạn. Vui lòng kiểm tra lại thông tin đăng nhập."
                
            profile_info = (
                f"Thông tin hồ sơ của bạn:\n"
                f"- Họ và tên: {action_result.get('name', 'Chưa cập nhật')}\n"
                f"- Email: {action_result.get('email', 'Chưa cập nhật')}\n"
                f"- Số điện thoại: {action_result.get('phone', 'Chưa cập nhật')}\n"
                f"- Địa chỉ: {action_result.get('address', 'Chưa cập nhật')}\n"
                f"- Ngày sinh: {action_result.get('dob', 'Chưa cập nhật')}\n"
                f"- Giới tính: {action_result.get('gender', 'Chưa cập nhật')}\n\n"
                f"Bạn có muốn cập nhật thông tin nào không? Nếu có, vui lòng cho tôi biết thông tin cần cập nhật."
            )
            return profile_info
        elif action == "update_profile":
            if "field" in action_result and "new_value" in action_result:
                field = action_result["field"]
                new_value = action_result["new_value"]
                old_value = action_result.get("old_value", "Chưa cập nhật")
                
                confirmation = (
                    f"Bạn có muốn thay đổi thông tin sau không?\n"
                    f"- Trường thông tin: {field}\n"
                    f"- Giá trị cũ: {old_value}\n"
                    f"- Giá trị mới: {new_value}\n\n"
                    f"Vui lòng xác nhận bằng cách trả lời 'đồng ý' hoặc 'không đồng ý'"
                )
                return confirmation
            return "Hồ sơ của bạn đã được cập nhật thành công."
        elif action == "get_preferences":
            preferences = action_result.get("preferences", {})
            categories = ", ".join(preferences.get("categories", []))
            brands = ", ".join(preferences.get("brands", []))
            price_range = preferences.get("price_range", {})
            return (
                f"Sở thích của bạn:\n"
                f"- Danh mục: {categories}\n"
                f"- Thương hiệu: {brands}\n"
                f"- Khoảng giá: {price_range.get('min', 0)} - {price_range.get('max', 0)} VNĐ"
            )
        elif action == "update_preferences":
            return "Sở thích của bạn đã được cập nhật thành công."
        else:
            return "Đã xảy ra lỗi khi xử lý yêu cầu của bạn."

    async def process_request(self, request: UserProfileRequest) -> UserProfileResponse:
        try:
            # Đảm bảo có user_id
            if not request.user_id:
                user_id = request.chat_id
            else:
                user_id = request.user_id
            
            # Phân tích yêu cầu
            prompt = f"""
            Hãy phân tích yêu cầu sau từ người dùng liên quan đến thông tin hồ sơ:
            "{request.message}"
            
            Nếu người dùng yêu cầu xem thông tin cá nhân, hãy trả về action "get_profile".
            Nếu người dùng muốn cập nhật thông tin, hãy trả về action "update_profile" với các thông tin cần cập nhật.
            
            Các thực thể đã được xác định:
            {request.entities if request.entities else 'Không có thông tin thực thể.'}
            """
            
            # Gọi agent để phân tích
            agent_response = await self.agent.a_generate_reply(messages=[{"role": "user", "content": prompt}])
            
            # Trích xuất hành động
            action_info = self._extract_action(agent_response)
            action = action_info.get("action", "get_profile")
            parameters = action_info.get("parameters", {})
            
            try:
                # Thực hiện hành động
                action_result = await self._execute_action(action, parameters, user_id)
                
                # Tạo nội dung phản hồi
                response_content = self._generate_response(action_result, action)
                
                # Lưu thông tin tương tác
                response_payload = ChatMessageCreate(
                    chat_id=request.chat_id,
                    role="assistant",
                    content=response_content,
                    metadata={"action": action, "result": "success"},
                    sender_type="assistant",
                    sender_id=user_id
                )
                MessageRepository.create_message(response_payload)
                
                return UserProfileResponse(
                    content=response_content,
                    user_data=action_result,
                    success=True
                )
            except HTTPException as he:
                error_content = f"Không thể truy cập thông tin hồ sơ: {he.detail}"
                response_payload = ChatMessageCreate(
                    chat_id=request.chat_id,
                    role="assistant",
                    content=error_content,
                    metadata={"action": action, "result": "error"},
                    sender_type="assistant",
                    sender_id=user_id
                )
                MessageRepository.create_message(response_payload)
                return UserProfileResponse(
                    content=error_content,
                    user_data={},
                    success=False
                )
            
        except Exception as e:
            logger.error(f"Lỗi trong user_profile_agent: {e}")
            error_content = "Đã xảy ra lỗi khi xử lý thông tin hồ sơ của bạn."
            try:
                response_payload = ChatMessageCreate(
                    chat_id=request.chat_id,
                    role="assistant",
                    content=error_content,
                    metadata={"action": "error", "result": "error"},
                    sender_type="assistant",
                    sender_id=request.user_id or request.chat_id
                )
                MessageRepository.create_message(response_payload)
            except:
                pass
            return UserProfileResponse(
                content=error_content,
                user_data={},
                success=False
            )
            
@router.post("/process", response_model=UserProfileResponse)
async def process_request(request: UserProfileRequest):
    db = None
    try:
        # Initialize database session
        from database import SessionLocal
        db = SessionLocal()
        
        # Khởi tạo agent với database session
        agent = UserProfileAgent(db)
        
        # Xử lý request
        response = await agent.process_request(request)
        return response
    except Exception as e:
        logger.error(f"Lỗi trong process_request endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Đảm bảo đóng database session
        if db:
            db.close() 