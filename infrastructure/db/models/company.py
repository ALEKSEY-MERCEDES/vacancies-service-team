import uuid
from datetime import datetime
from sqlalchemy import text
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.db.base import Base


class Company(Base):
    __tablename__ = "companies"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = mapped_column(String(255), unique=True, nullable=False)
    is_active = mapped_column(Boolean, server_default="true")
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())

