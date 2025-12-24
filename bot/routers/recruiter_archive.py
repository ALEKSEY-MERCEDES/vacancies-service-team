from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, func

from infrastructure.db.session import get_session
from infrastructure.db.models import User, Recruiter, Vacancy, Application
from bot.keyboards.recruiter_archive import recruiter_archive_kb

router = Router()


@router.callback_query(F.data == "r:archive")
async def recruiter_archive(cb: CallbackQuery):
    tg_id = cb.from_user.id

    async for session in get_session():
        recruiter_res = await session.execute(
            select(Recruiter)
            .join(User, User.id == Recruiter.user_id)
            .where(User.telegram_id == tg_id)
        )
        recruiter = recruiter_res.scalar_one_or_none()
        if not recruiter:
            await cb.answer("Вы не рекрутер", show_alert=True)
            return

        vacancies_res = await session.execute(
            select(Vacancy)
            .where(
                Vacancy.recruiter_id == recruiter.id,
                Vacancy.status == "closed",
            )
            .order_by(Vacancy.created_at.desc())
        )
        vacancies = vacancies_res.scalars().all()

        vacancies_ui = []
        for v in vacancies:
            cnt_res = await session.execute(
                select(func.count(Application.id))
                .where(Application.vacancy_id == v.id)
            )
            vacancies_ui.append({
                "id": str(v.id),
                "title": v.title,
                "applications_count": int(cnt_res.scalar() or 0),
            })

    if not vacancies_ui:
        await cb.message.answer("🗄 Архив пуст — закрытых вакансий пока нет.")
        await cb.answer()
        return

    await cb.message.answer(
        "🗄 <b>Архив вакансий</b>\n\nНажми на вакансию, чтобы открыть карточку и при желании переоткрыть.",
        reply_markup=recruiter_archive_kb(vacancies_ui),
        parse_mode="HTML",
    )
    await cb.answer()
