from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.models import User, Recruiter, Company, RecruiterCompany


async def get_recruiter_bundle(session: AsyncSession, telegram_id: int):
    """
    Получает связку User + Recruiter + Company для рекрутера.

    Возвращает кортеж: (user, recruiter, company)
    Если что-то не найдено — возвращает None в соответствующей позиции.
    """
    # 1. Находим User
    res = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = res.scalar_one_or_none()

    if not user:
        return None, None, None

    # 2. Находим Recruiter
    res = await session.execute(
        select(Recruiter).where(Recruiter.user_id == user.id)
    )
    recruiter = res.scalar_one_or_none()

    if not recruiter:
        return user, None, None

    # 3. Находим Company через связующую таблицу
    res = await session.execute(
        select(Company)
        .join(RecruiterCompany, RecruiterCompany.company_id == Company.id)
        .where(RecruiterCompany.recruiter_id == recruiter.id)
        .limit(1)
    )
    company = res.scalar_one_or_none()

    return user, recruiter, company