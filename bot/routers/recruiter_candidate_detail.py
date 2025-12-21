from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, update

from infrastructure.db.session import get_session
from infrastructure.db.models import Candidate, Application
from bot.keyboards.recruiter_candidate_detail import recruiter_candidate_detail_kb

router = Router()


@router.callback_query(F.data.startswith("candidate:"))
async def recruiter_candidate_detail(callback: CallbackQuery):
    _, candidate_id, vacancy_id = callback.data.split(":")

    async for session in get_session():
        # 1) кандидат
        cand_res = await session.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        candidate = cand_res.scalar_one_or_none()
        if not candidate:
            await callback.message.answer("❌ Кандидат не найден")
            return

        # 2) пометить отклик как viewed (если был sent)
        await session.execute(
            update(Application)
            .where(
                Application.vacancy_id == vacancy_id,
                Application.candidate_id == candidate_id,
                Application.status == "sent",
            )
            .values(status="viewed")
        )
        await session.commit()

    text = (
        f"👤 {candidate.full_name or 'Без имени'}\n"
        f"Возраст: {candidate.age or '—'}\n\n"
        f"Навыки:\n{candidate.skills or '—'}\n\n"
        f"Текущая компания: {candidate.current_company or '—'}"
    )

    await callback.message.answer(
        text,
        reply_markup=recruiter_candidate_detail_kb(candidate_id, vacancy_id),
    )

    # Если есть резюме — отправим файлом след. сообщением
    if candidate.resume_file_id:
        await callback.message.answer_document(candidate.resume_file_id)
