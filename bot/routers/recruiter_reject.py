from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, update

from infrastructure.db.session import get_session
from infrastructure.db.models import Candidate, User, Application
from bot.keyboards.recruiter_reject import recruiter_reject_confirm_kb

router = Router()


@router.callback_query(F.data.startswith("reject_confirm:"))
async def reject_confirm(callback: CallbackQuery):
    _, candidate_id, vacancy_id = callback.data.split(":")
    await callback.message.answer(
        "⚠️ Вы уверены, что хотите отказать? Кандидату придёт стандартное уведомление.",
        reply_markup=recruiter_reject_confirm_kb(candidate_id, vacancy_id),
    )


@router.callback_query(F.data.startswith("reject:"))
async def reject_do(callback: CallbackQuery):
    _, candidate_id, vacancy_id = callback.data.split(":")

    async for session in get_session():
        # tg кандидата
        res = await session.execute(
            select(User.telegram_id)
            .select_from(Candidate)
            .join(User, User.id == Candidate.user_id)
            .where(Candidate.id == candidate_id)
        )
        candidate_tg = res.scalar_one_or_none()

        await session.execute(
            update(Application)
            .where(
                Application.vacancy_id == vacancy_id,
                Application.candidate_id == candidate_id,
            )
            .values(status="rejected")
        )
        await session.commit()

    if candidate_tg:
        await callback.message.bot.send_message(
            chat_id=candidate_tg,
            text="Спасибо за отклик! К сожалению, на данном этапе мы решили продолжить с другими кандидатами.",
        )

    await callback.message.answer("✅ Отказ отправлен.")
