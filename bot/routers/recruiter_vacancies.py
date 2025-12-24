from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, func

from infrastructure.db.session import get_session
from infrastructure.db.models import User, Recruiter, Vacancy, Application
from bot.keyboards.recruiter_vacancies import recruiter_vacancies_kb

router = Router()


@router.callback_query(F.data == "r:my_vacancies")
async def recruiter_vacancies(callback: CallbackQuery):
    tg_id = callback.from_user.id

    async for session in get_session():
        # 1️⃣ Находим рекрутера
        recruiter_result = await session.execute(
            select(Recruiter)
            .join(User)
            .where(User.telegram_id == tg_id)
        )
        recruiter = recruiter_result.scalar_one_or_none()

        if not recruiter:
            await callback.message.answer("❌ Рекрутер не найден")
            return

        # 2️⃣ Получаем вакансии рекрутера
        vacancies_result = await session.execute(
            select(Vacancy).where(Vacancy.recruiter_id == recruiter.id)
        )
        vacancies = vacancies_result.scalars().all()

        # 3️⃣ Готовим данные для UI
        vacancies_ui = []

        for vacancy in vacancies:
            count_result = await session.execute(
                select(func.count(Application.id))
                .where(Application.vacancy_id == vacancy.id)
            )
            applications_count = count_result.scalar() or 0

            vacancies_ui.append(
                {
                    "id": str(vacancy.id),
                    "title": vacancy.title,
                    "applications_count": applications_count,
                }
            )

    # 4️⃣ Отправляем сообщение
    await callback.message.answer(
        "📂 Управление вакансиями\n\n"
        "Нажмите на вакансию, чтобы посмотреть детали.",
        reply_markup=recruiter_vacancies_kb(vacancies_ui),
    )
    await callback.answer()  # ✅ вот это добавь