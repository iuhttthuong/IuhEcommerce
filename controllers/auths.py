from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from repositories.customers import CustomerRepository
from typing import Optional
import jwt
from env import env
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/api/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    id: int


class AuthMeResponse(BaseModel):
    customer_id: int
    customer_fname: str
    customer_lname: str
    customer_mail: str
    customer_address: str
    customer_phone: str
    customer_dob: datetime
    customer_gender: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


security = HTTPBearer()


def verify_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, env.JWT_SECRET, algorithms=["HS256"])
        return payload.get("customer_id")
    except jwt.ExpiredSignatureError:
        # Token hết hạn
        return None
    except Exception:
        # Token không hợp lệ
        return None


@router.get("/me", response_model=AuthMeResponse)
async def get_me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    customer_id = verify_token(token)
    if not customer_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn.",
        )
    customer = CustomerRepository.get_one(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thông tin khách hàng.",
        )
    # customer.model_dump() sẽ chuyển về dict (nếu là Pydantic model)
    return AuthMeResponse(**customer.model_dump())


@router.post("/token", response_model=TokenResponse)
async def generate_token(data: LoginRequest):
    customer_id = data.id
    if not customer_id:
        raise HTTPException(status_code=400, detail="customer_id is required")
    customer = CustomerRepository.get_by_id(customer_id)
    if not customer:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy thông tin khách hàng."
        )
    # Sử dụng datetime.now(timezone.utc) để đảm bảo timezone-aware và không bị warning
    payload = {
        "customer_id": customer_id,
        "exp": (
            datetime.now(timezone.utc) + timedelta(days=7)
        ).timestamp(),  # hết hạn sau 7 ngày
    }
    token = jwt.encode(payload, env.JWT_SECRET, algorithm="HS256")
    print(await get_me(token))
    
    return TokenResponse(access_token=token)
