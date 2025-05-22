from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from datetime import datetime
from sqlalchemy.orm import declarative_base, registry
from sqlalchemy import MetaData

# Create a shared metadata and registry
metadata = MetaData()
mapper_registry = registry(metadata=metadata)

# Create the base class
Base = declarative_base(metadata=metadata)

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )