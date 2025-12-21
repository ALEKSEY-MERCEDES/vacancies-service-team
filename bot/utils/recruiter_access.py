from sqlalchemy import select

from infrastructure.db.models import User, Recruiter, RecruiterCompany, Company


async def get_recruiter_bundle(session, tg_id: int):
    """
    Возвращает: (user, recruiter, company|None)
    """
    res = await session.execute(select(User).where(User.telegram_id == tg_id))
    user = res.scalar_one_or_none()
    if not user:
        return None, None, None

    res = await session.execute(select(Recruiter).where(Recruiter.user_id == user.id))
    recruiter = res.scalar_one_or_none()
    if not recruiter:
        return user, None, None

    # company (если привязана)
    res = await session.execute(
        select(Company)
        .join(RecruiterCompany, RecruiterCompany.company_id == Company.id)
        .where(RecruiterCompany.recruiter_id == recruiter.id)
    )
    company = res.scalar_one_or_none()

    return user, recruiter, company
