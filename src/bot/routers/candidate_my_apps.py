from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.infrastructure.db.session import get_db
from src.infrastructure.db.models import User, Candidate, Application, Vacancy, Company
from src.bot.keyboards.candidate_my_apps import candidate_my_apps_kb, candidate_app_detail_kb
from src.bot.keyboards.common import candidate_menu

router = Router()

PER_PAGE = 8

STATUS_ICON = {
    "sent": "🟢",
    "viewed": "👀",
    "invited": "✅",
    "rejected": "❌",
}


async def _get_candidate(session, tg_id: int):
    res = await session.execute(
        select(Candidate)
        .join(User, User.id == Candidate.user_id)
        .where(User.telegram_id == tg_id)
    )
    return res.scalar_one_or_none()


@router.callback_query(F.data == "c:my_apps")
@router.callback_query(F.data.startswith("c:my_apps:"))
async def my_apps(cb: CallbackQuery):
    page = 0
    if cb.data.startswith("c:my_apps:"):
        page = int(cb.data.split(":")[2])

    async with get_db() as session:
        cand = await _get_candidate(session, cb.from_user.id)
        if not cand:
            await cb.message.answer("Сначала зарегистрируйтесь как соискатель.")
            await cb.answer()
            return

        q = (
            select(Application, Vacancy, Company)
            .join(Vacancy, Vacancy.id == Application.vacancy_id)
            .outerjoin(Company, Company.id == Vacancy.company_id)
            .where(Application.candidate_id == cand.id)
            .order_by(Application.created_at.desc())
            .offset(page * PER_PAGE)
            .limit(PER_PAGE + 1)
        )
        res = await session.execute(q)
        rows = list(res.all())

        has_next = len(rows) > PER_PAGE
        rows = rows[:PER_PAGE]
        has_prev = page > 0

        if not rows and page == 0:
            await cb.message.answer("У вас пока нет откликов 🙂", reply_markup=candidate_menu())
            await cb.answer()
            return

        items = []
        for app, vac, comp in rows:
            items.append({
                "app_id": str(app.id),
                "title": vac.title,
                "company": comp.name if comp else "—",
                "status_icon": STATUS_ICON.get(app.status, "⚪️"),
            })

        await cb.message.answer(
            f"📨 <b>Мои отклики</b>\n\n"
            f"Статусы: 🟢 отправлен · 👀 просмотрен · ✅ приглашение · ❌ отказ",
            reply_markup=candidate_my_apps_kb(items, page, has_prev, has_next),
            parse_mode="HTML",
        )
        await cb.answer()


@router.callback_query(F.data.startswith("c:app:"))
async def my_app_detail(cb: CallbackQuery):
    app_id = cb.data.split(":")[2]

    async with get_db() as session:
        cand = await _get_candidate(session, cb.from_user.id)
        if not cand:
            await cb.message.answer("Сначала зарегистрируйтесь как соискатель.")
            await cb.answer()
            return

        res = await session.execute(
            select(Application, Vacancy, Company)
            .join(Vacancy, Vacancy.id == Application.vacancy_id)
            .outerjoin(Company, Company.id == Vacancy.company_id)
            .where(Application.id == app_id)
            .where(Application.candidate_id == cand.id)
        )
        row = res.first()

        if not row:
            await cb.answer("Отклик не найден", show_alert=True)
            return

        app, vac, comp = row
        icon = STATUS_ICON.get(app.status, "⚪️")
        company_name = comp.name if comp else "—"

        message_text = ""
        if app.message:
            message_text = f"\n\n💬 <b>Ваше сообщение:</b>\n<i>{app.message}</i>"

        text = (
            f"{icon} <b>{vac.title}</b>\n"
            f"🏢 {company_name}\n\n"
            f"📌 Статус: <b>{app.status}</b>\n"
            f"📅 Дата отклика: {app.created_at:%d.%m.%Y %H:%M}"
            f"{message_text}\n\n"
            f"📝 <b>Описание вакансии:</b>\n{vac.description}"
        )

        await cb.message.answer(
            text,
            parse_mode="HTML",
            reply_markup=candidate_app_detail_kb(app_id, app.status)
        )
        await cb.answer()