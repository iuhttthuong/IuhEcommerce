from datetime import datetime, timedelta, UTC
from pydantic import BaseModel
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from pydantic import ValidationError
from env import env
from typing import Union, Any

SECURITY_ALGORITHM = 'HS256'
SECRET_KEY = env.JWT_SECRET

reusable_oauth2 = HTTPBearer(scheme_name='Authorization')

class LoginRequest(BaseModel):
    username: str
    password: str

def verify_password(username, password):
    return username == 'admin' and password == 'admin'

def validate_token(token: str) -> str:
    """
    Decode JWT token to get username => return username
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[SECURITY_ALGORITHM])
        exp = payload.get('exp')
        now_ts = datetime.now(UTC).timestamp()
        if exp is not None and exp < now_ts:
            raise HTTPException(status_code=403, detail="Token expired")
        return payload.get('username')
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials",
        )

def generate_token(username: Union[str, Any]) -> str:
    expire = datetime.now(UTC) + timedelta(seconds=60 * 60 * 24 * 3)  # 3 days
    to_encode = {
        "exp": expire,
        "username": username
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=SECURITY_ALGORITHM)
    return encoded_jwt

def login(request_data: LoginRequest):
    print(f'[x] request_data: {request_data.__dict__}')
    if verify_password(username=request_data.username, password=request_data.password):
        token = generate_token(request_data.username)
        print(validate_token(token))  # Test validate_token
        return {
            'token': token
        }
    else:
        raise HTTPException(status_code=404, detail="User not found")

# TEST:
if __name__ == '__main__':
    print(login(LoginRequest(username="admin", password="admin")))
