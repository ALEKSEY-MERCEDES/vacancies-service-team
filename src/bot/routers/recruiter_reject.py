from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, update

from src.infrastructure.db.session import get_session
from src.infrastructure.db.models import Candidate, User, Application, Vacancy
from src.bot.keyboards.recruiter_reject import recruiter_reject_confirm_kb
from src.bot.utils.callbacks import unpack_uuid
from src.bot.routers.recruiter_vacancy_detail import render_responses

router = Router()


@router.callback_query(F.data.startswith("reject_confirm:"))
async def reject_confirm(cb: CallbackQuery):
    _, c_short, v_short = cb.data.split(":")
    await cb.message.answer(
        "⚠️ Вы уверены, что хотите отказать? Кандидату придёт стандартное уведомление.",
        reply_markup=recruiter_reject_confirm_kb(c_short, v_short),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("reject:"))
async def reject_do(cb: CallbackQuery):
    _, c_short, v_short = cb.data.split(":")
    candidate_id = unpack_uuid(c_short)
    vacancy_id = unpack_uuid(v_short)

    candidate_tg = None
    vacancy_title = "вакансию"

    async for session in get_session():
        tg_res = await session.execute(
            select(User.telegram_id)
            .select_from(Candidate)
            .join(User, User.id == Candidate.user_id)
            .where(Candidate.id == candidate_id)
        )
        candidate_tg = tg_res.scalar_one_or_none()

        vac_res = await session.execute(select(Vacancy.title).where(Vacancy.id == vacancy_id))
        vacancy_title = vac_res.scalar_one_or_none() or vacancy_title

        await session.execute(
            update(Application)
            .where(
                Application.vacancy_id == vacancy_id,
                Application.candidate_id == candidate_id,
            )
            .values(status="rejected")
        )
        await session.commit()

        await render_responses(cb, session, vacancy_id, edit=True)

    if candidate_tg:
        await cb.bot.send_message(
            chat_id=candidate_tg,
            text=(
                f"Спасибо за отклик на <b>{vacancy_title}</b>!\n"
                f"К сожалению, на данном этапе мы решили продолжить с другими кандидатами."
            ),
            parse_mode="HTML",
        )

    await cb.answer("✅ Отказ отправлен", show_alert=True)