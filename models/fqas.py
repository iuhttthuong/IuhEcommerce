from datetime import datetime
from sqlalchemy import ForeignKey, DECIMAL, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base

class FQA(Base):
    __tablename__ = "fqas"
    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column(nullable=False)
    answer: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
class FQACreate(BaseModel):
    question: str
    answer: str

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class FQAModel(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True