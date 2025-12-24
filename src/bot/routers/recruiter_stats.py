from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, func, case

from src.infrastructure.db.session import get_session
from src.infrastructure.db.models import User, Recruiter, Vacancy, Application
from src.bot.keyboards.recruiter_stats import recruiter_stats_kb

router = Router()


@router.callback_query(F.data == "r:stats")
async def recruiter_stats(cb: CallbackQuery):
    tg_id = cb.from_user.id

    async for session in get_session():

        recruiter_res = await session.execute(
            select(Recruiter)
            .join(User, User.id == Recruiter.user_id)
            .where(User.telegram_id == tg_id)
        )
        recruiter = recruiter_res.scalar_one_or_none()
        if not recruiter:
            await cb.answer("Рекрутер не найден", show_alert=True)
            return

        vac_counts = await session.execute(
            select(
                func.count(Vacancy.id).label("total"),
                func.sum(case((Vacancy.status == "open", 1), else_=0)).label("open"),
                func.sum(case((Vacancy.status != "open", 1), else_=0)).label("closed"),
            )
            .where(Vacancy.recruiter_id == recruiter.id)
        )
        total_v, open_v, closed_v = vac_counts.one()
        total_v = total_v or 0
        open_v = open_v or 0
        closed_v = closed_v or 0

        app_counts = await session.execute(
            select(
                func.count(Application.id).label("total"),
                func.sum(case((Application.status == "sent", 1), else_=0)).label("sent"),
                func.sum(case((Application.status == "viewed", 1), else_=0)).label("viewed"),
                func.sum(case((Application.status == "invited", 1), else_=0)).label("invited"),
                func.sum(case((Application.status == "rejected", 1), else_=0)).label("rejected"),
            )
            .select_from(Application)
            .join(Vacancy, Vacancy.id == Application.vacancy_id)
            .where(Vacancy.recruiter_id == recruiter.id)
        )
        total_a, sent_a, viewed_a, invited_a, rejected_a = app_counts.one()
        total_a = total_a or 0
        sent_a = sent_a or 0
        viewed_a = viewed_a or 0
        invited_a = invited_a or 0
        rejected_a = rejected_a or 0

    text = (
        "📊 <b>Статистика рекрутера</b>\n\n"
        f"💼 Вакансии:\n"
        f"• Всего: <b>{total_v}</b>\n"
        f"• Активные: <b>{open_v}</b>\n"
        f"• В архиве: <b>{closed_v}</b>\n\n"
        f"📩 Отклики:\n"
        f"• Всего: <b>{total_a}</b>\n"
        f"• Новые: <b>{sent_a}</b>\n"
        f"• Просмотрено: <b>{viewed_a}</b>\n"
        f"• Приглашены: <b>{invited_a}</b>\n"
        f"• Отказы: <b>{rejected_a}</b>\n"
    )

    await cb.message.answer(text, reply_markup=recruiter_stats_kb(), parse_mode="HTML")
    await cb.answer()