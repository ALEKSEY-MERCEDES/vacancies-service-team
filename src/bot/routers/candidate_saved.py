from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, delete, and_
import uuid

from src.infrastructure.db.session import get_db
from src.infrastructure.db.models import User, Candidate, Vacancy, Company, Reaction
from src.bot.keyboards.candidate_saved import candidate_saved_kb, candidate_saved_detail_kb
from src.bot.keyboards.common import candidate_menu

router = Router()

PER_PAGE = 8


async def _get_candidate(session, tg_id: int) -> Candidate | None:
    res = await session.execute(
        select(Candidate)
        .join(User, User.id == Candidate.user_id)
        .where(User.telegram_id == tg_id)
    )
    return res.scalar_one_or_none()


@router.callback_query(F.data == "c:saved")
@router.callback_query(F.data.startswith("c:saved:"))
async def saved_vacancies(cb: CallbackQuery):
    """Список сохранённых вакансий (лайки)"""
    page = 0
    if ":" in cb.data and cb.data.count(":") >= 2:
        try:
            page = int(cb.data.split(":")[2])
        except (ValueError, IndexError):
            page = 0

    async with get_db() as session:
        cand = await _get_candidate(session, cb.from_user.id)
        if not cand:
            await cb.message.answer("Сначала зарегистрируйтесь как соискатель.")
            await cb.answer()
            return

        q = (
            select(Reaction, Vacancy, Company)
            .join(Vacancy, Vacancy.id == Reaction.vacancy_id)
            .join(Company, Company.id == Vacancy.company_id)
            .where(Reaction.candidate_id == cand.id)
            .where(Reaction.value == "like")
            .order_by(Reaction.created_at.desc())
            .offset(page * PER_PAGE)
            .limit(PER_PAGE + 1)
        )
        res = await session.execute(q)
        rows = list(res.all())

        has_next = len(rows) > PER_PAGE
        rows = rows[:PER_PAGE]
        has_prev = page > 0

        if not rows and page == 0:
            await cb.message.answer(
                "⭐ <b>Сохранённые вакансии</b>\n\n"
                "Пока пусто. Нажмите 👍 на вакансии чтобы сохранить.",
                parse_mode="HTML",
                reply_markup=candidate_menu()
            )
            await cb.answer()
            return

        items = []
        for reaction, vac, comp in rows:
            items.append({
                "vacancy_id": str(vac.id),
                "title": vac.title,
                "company": comp.name,
            })

        await cb.message.answer(
            f"⭐ <b>Сохранённые вакансии</b>\n\n"
            f"Всего: {len(items)}",
            reply_markup=candidate_saved_kb(items, page, has_prev, has_next),
            parse_mode="HTML",
        )
        await cb.answer()


@router.callback_query(F.data.startswith("c:saved_detail:"))
async def saved_detail(cb: CallbackQuery):
    """Детали сохранённой вакансии"""
    vacancy_id_str = cb.data.split(":")[2]

    try:
        vacancy_uuid = uuid.UUID(vacancy_id_str)
    except ValueError:
        await cb.answer("Ошибка", show_alert=True)
        return

    async with get_db() as session:
        res = await session.execute(
            select(Vacancy, Company)
            .join(Company, Company.id == Vacancy.company_id)
            .where(Vacancy.id == vacancy_uuid)
        )
        row = res.first()

        if not row:
            await cb.answer("Вакансия не найдена", show_alert=True)
            return

        vac, comp = row

        status = "🟢 Активна" if vac.status == "open" else "🔴 Закрыта"
        text = (
            f"⭐ <b>{vac.title}</b>\n"
            f"🏢 {comp.name}\n"
            f"📌 {status}\n\n"
            f"{vac.description}"
        )

        await cb.message.answer(
            text,
            reply_markup=candidate_saved_detail_kb(vacancy_id_str),
            parse_mode="HTML"
        )
        await cb.answer()


@router.callback_query(F.data.startswith("c:unsave:"))
async def unsave_vacancy(cb: CallbackQuery):
    """Убрать из сохранённых (удалить лайк)"""
    vacancy_id_str = cb.data.split(":")[2]

    try:
        vacancy_uuid = uuid.UUID(vacancy_id_str)
    except ValueError:
        await cb.answer("Ошибка", show_alert=True)
        return

    async with get_db() as session:
        cand = await _get_candidate(session, cb.from_user.id)
        if not cand:
            await cb.answer("Ошибка", show_alert=True)
            return

        await session.execute(
            delete(Reaction).where(
                and_(
                    Reaction.candidate_id == cand.id,
                    Reaction.vacancy_id == vacancy_uuid,
                    Reaction.value == "like"
                )
            )
        )
        await session.commit()

        await cb.answer("💔 Убрано из сохранённых", show_alert=True)

    await saved_vacancies(cb)