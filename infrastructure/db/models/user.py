import uuid
from datetime import datetime

from sqlalchemy import BigInteger, String, DateTime, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),  # ← ВОТ ТУТ
    )

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)


