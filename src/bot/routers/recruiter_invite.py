from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, update

from src.infrastructure.db.session import get_session
from src.infrastructure.db.models import Application, Candidate, User, Vacancy
from src.bot.utils.callbacks import unpack_uuid
from src.bot.routers.recruiter_vacancy_detail import render_responses

router = Router()


@router.callback_query(F.data.startswith("invite:"))
async def invite_candidate(cb: CallbackQuery):
    # invite:<c_short>:<v_short>
    _, c_short, v_short = cb.data.split(":")
    candidate_id = unpack_uuid(c_short)
    vacancy_id = unpack_uuid(v_short)

    candidate_tg = None
    vacancy_title = "Вакансия"

    async for session in get_session():
        app_res = await session.execute(
            select(Application).where(
                Application.candidate_id == candidate_id,
                Application.vacancy_id == vacancy_id,
            )
        )
        app = app_res.scalar_one_or_none()
        if not app:
            await cb.answer("Отклик не найден", show_alert=True)
            return

        await session.execute(
            update(Application).where(Application.id == app.id).values(status="invited")
        )
        await session.commit()

        tg_res = await session.execute(
            select(User.telegram_id)
            .select_from(Candidate)
            .join(User, User.id == Candidate.user_id)
            .where(Candidate.id == candidate_id)
        )
        candidate_tg = tg_res.scalar_one_or_none()

        vac_res = await session.execute(select(Vacancy.title).where(Vacancy.id == vacancy_id))
        vacancy_title = vac_res.scalar_one_or_none() or vacancy_title

        # ✅ возвращаем рекрутера в список откликов (обновляем текущий экран)
        await render_responses(cb, session, vacancy_id, edit=True)

    if candidate_tg:
        await cb.bot.send_message(
            candidate_tg,
            f"📞 Вас пригласили на вакансию: <b>{vacancy_title}</b>",
            parse_mode="HTML",
        )

    await cb.answer("✅ Кандидат приглашён", show_alert=True)