import pytest
from src.infrastructure.db.models import User, Recruiter, Company, RecruiterCompany


@pytest.mark.asyncio
async def test_recruiter_and_company_link(async_session):
    user = User(
        telegram_id=333,
        role="recruiter",
    )
    recruiter = Recruiter(
        user=user,
        full_name="HR",
        position="HR Manager",
    )
    company = Company(name="TestCorp")

    async_session.add_all([user, recruiter, company])
    await async_session.flush()

    link = RecruiterCompany(
        recruiter_id=recruiter.id,
        company_id=company.id,
    )
    async_session.add(link)
    await async_session.commit()

    assert recruiter.id is not None
    assert company.is_active is True
