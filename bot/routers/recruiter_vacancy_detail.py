from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, func

from infrastructure.db.session import get_session
from infrastructure.db.models import Vacancy, Application
from bot.keyboards.recruiter_vacancy_detail import recruiter_vacancy_detail_kb

router = Router()


@router.callback_query(F.data.startswith("vacancy:"))
async def vacancy_detail(callback: CallbackQuery):
    vacancy_id = callback.data.split(":")[1]

    async for session in get_session():
        vacancy_result = await session.execute(
            select(Vacancy).where(Vacancy.id == vacancy_id)
        )
        vacancy = vacancy_result.scalar_one_or_none()

        if not vacancy:
            await callback.message.answer("❌ Вакансия не найдена")
            return

        apps_result = await session.execute(
            select(func.count(Application.id))
            .where(Application.vacancy_id == vacancy.id)
        )
        applications_count = apps_result.scalar() or 0

    status_text = "🟢 Активна" if vacancy.status == "open" else "🔴 Закрыта"

    await callback.message.answer(
        f"💼 {vacancy.title}\n"
        f"Статус: {status_text}\n\n"
        f"Всего откликов: {applications_count}\n"
        f"Опубликована: {vacancy.created_at:%d.%m.%Y}",
        reply_markup=recruiter_vacancy_detail_kb(str(vacancy.id)),
    )
