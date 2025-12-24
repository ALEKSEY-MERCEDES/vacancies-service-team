import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.base import Base


class RecruiterApplication(Base):
    __tablename__ = "recruiter_applications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    application_number: Mapped[int] = mapped_column(
        nullable=False,
        unique=True,
        comment="Порядковый номер заявки для отображения",
    )

    recruiter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recruiters.id", ondelete="CASCADE"),
        nullable=False,
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        comment="Компания, в которую подается заявка",
    )

    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        server_default="pending",
        comment="pending | approved | rejected",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Когда рассмотрена",
    )

    recruiter = relationship("Recruiter", backref="applications",
                             lazy="joined")
    company = relationship("Company", lazy="joined")