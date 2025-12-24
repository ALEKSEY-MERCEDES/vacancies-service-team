import pytest
from src.infrastructure.db.models import (
    User, Recruiter, Company, Vacancy
)


@pytest.mark.asyncio
async def test_create_vacancy(async_session):
    user = User(telegram_id=444, role="recruiter")
    recruiter = Recruiter(user=user)
    company = Company(name="VacancyCorp")

    async_session.add_all([user, recruiter, company])
    await async_session.flush()

    vacancy = Vacancy(
        title="Python Dev",
        description="Backend",
        salary_from=100000,
        salary_to=200000,
        city="Moscow",
        company_id=company.id,
        recruiter_id=recruiter.id,
    )

    async_session.add(vacancy)
    await async_session.commit()

    assert vacancy.status == "open"
    assert vacancy.company.name == "VacancyCorp"
