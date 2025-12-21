from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, func

from infrastructure.db.session import get_session
from infrastructure.db.models import User, Recruiter, Vacancy, Application

router = Router()


@router.callback_query(F.data == "recruiter_main")
async def recruiter_main(callback: CallbackQuery):
    tg_id = callback.from_user.id

    async for session in get_session():
        res = await session.execute(select(User).where(User.telegram_id == tg_id))
        user = res.scalar_one_or_none()
        if not user or user.role != "recruiter":
            await callback.answer("Вы не рекрутер", show_alert=True)
            return

        res = await session.execute(select(Recruiter).where(Recruiter.user_id == user.id))
        recruiter = res.scalar_one_or_none()
        if not recruiter:
            await callback.message.answer("Сначала пройдите регистрацию рекрутера.")
            return

        # Активные вакансии
        res = await session.execute(
            select(func.count(Vacancy.id)).where(
                Vacancy.recruiter_id == recruiter.id,
                Vacancy.status == "open",
            )
        )
        active_vacancies = res.scalar_one()

        # Новые отклики (sent)
        res = await session.execute(
            select(func.count(Application.id))
            .join(Vacancy, Vacancy.id == Application.vacancy_id)
            .where(
                Vacancy.recruiter_id == recruiter.id,
                Application.status == "sent",
            )
        )
        new_apps = res.scalar_one()

    await callback.message.answer(
        f"💼 Кабинет рекрутера\n\n"
        f"Статус: {recruiter.status}\n"
        f"📄 Активных вакансий: {active_vacancies}\n"
        f"📩 Новых откликов: {new_apps}"
    )
