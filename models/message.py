from typing import Optional
from pydantic import BaseModel

class UpdateMessagePayload(BaseModel):
    content: Optional[str]
    role: Optional[str]
    is_read: Optional[bool]


