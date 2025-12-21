from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select

from infrastructure.db.session import get_session
from infrastructure.db.models import Application, Candidate
from bot.keyboards.recruiter_responses import recruiter_responses_kb

router = Router()


@router.callback_query(F.data.startswith("vacancy_responses:"))
async def vacancy_responses(callback: CallbackQuery):
    vacancy_id = callback.data.split(":")[1]

    async for session in get_session():
        result = await session.execute(
            select(Application, Candidate)
            .join(Candidate, Candidate.id == Application.candidate_id)
            .where(Application.vacancy_id == vacancy_id)
        )

        applications_ui = []

        for app, candidate in result.all():
            applications_ui.append(
                {
                    "candidate_id": str(candidate.id),
                    "full_name": candidate.full_name or "Без имени",
                    "age": candidate.age or "?",
                    "status": app.status,
                }
            )

    await callback.message.answer(
        f"📩 Отклики на вакансию\n\n"
        f"Всего кандидатов: {len(applications_ui)}",
        reply_markup=recruiter_responses_kb(applications_ui, vacancy_id),
    )
