# tests/integration/test_notify_recruiter.py
import pytest
from unittest.mock import AsyncMock

from src.infrastructure.db.models import (
    User, Recruiter, Company, Vacancy
)
from src.bot.utils.notify_recruiter import notify_recruiter_new_application


@pytest.mark.asyncio
async def test_notify_recruiter(async_session):
    bot = AsyncMock()

    user = User(telegram_id=777, role="recruiter")
    recruiter = Recruiter(user=user)
    company = Company(name="NotifyCorp")
    vacancy = Vacancy(
        title="DevOps",
        description="Cloud",
        company=company,
        recruiter=recruiter,
    )

    async_session.add_all([user, recruiter, vacancy])
    await async_session.commit()

    await notify_recruiter_new_application(
        bot=bot,
        recruiter_id=recruiter.id,
        vacancy_id=vacancy.id,
        candidate_name="Alex",
    )

    bot.send_message.assert_called_once()
