import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    full_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="ФИО соискателя",
    )

    age: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Возраст",
    )

    skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Навыки (через запятую или текстом)",
    )

    current_company: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Текущее место работы",
    )

    resume_file_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Telegram file_id резюме",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
