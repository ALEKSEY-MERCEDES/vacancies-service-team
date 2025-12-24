from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.infrastructure.db.session import get_db
from src.infrastructure.db.models import User, Candidate, Vacancy, Reaction, CandidateCompanyBlock
from src.bot.keyboards.candidate_vacancies import candidate_vacancy_feed_kb
from src.bot.keyboards.common import candidate_menu

router = Router()

PER_PAGE = 1


async def _get_candidate(session, tg_id: int) -> Candidate | None:
    res = await session.execute(
        select(Candidate)
        .join(User, User.id == Candidate.user_id)
        .where(User.telegram_id == tg_id)
    )
    return res.scalar_one_or_none()


async def _get_feed(session, candidate_id, page: int):
    blocked_company_ids = select(CandidateCompanyBlock.company_id).where(
        CandidateCompanyBlock.candidate_id == candidate_id
    )

    q = (
        select(Vacancy)
        .where(Vacancy.status == "open")
        .where(Vacancy.company_id.not_in(blocked_company_ids))
        .order_by(Vacancy.created_at.desc())
        .offset(page * PER_PAGE)
        .limit(PER_PAGE + 1)
    )

    res = await session.execute(q)
    items = list(res.scalars().all())

    has_next = len(items) > PER_PAGE
    items = items[:PER_PAGE]
    has_prev = page > 0

    return items, has_prev, has_next


def _format_vacancy(v: Vacancy) -> str:
    company_name = v.company.name if v.company else "—"
    status = "🟢 Активна" if v.status == "open" else "🔴 Закрыта"

    return (
        f"💼 <b>{v.title}</b>\n"
        f"🏢 {company_name}\n"
        f"📌 {status}\n\n"
        f"{v.description}"
    )


@router.callback_query(F.data == "vacancies")
async def candidate_feed_start(cb: CallbackQuery):
    async with get_db() as session:
        cand = await _get_candidate(session, cb.from_user.id)

        if not cand:
            await cb.message.answer("Сначала зарегистрируйтесь как соискатель через меню роли.")
            await cb.answer()
            return

        page = 0
        items, has_prev, has_next = await _get_feed(session, cand.id, page)

        if not items:
            await cb.message.answer("Пока нет доступных вакансий 😕", reply_markup=candidate_menu())
            await cb.answer()
            return

        v = items[0]
        await cb.message.answer(
            _format_vacancy(v),
            reply_markup=candidate_vacancy_feed_kb(str(v.id), page, has_prev, has_next),
            parse_mode="HTML",
        )
        await cb.answer()


@router.callback_query(F.data.startswith("c:feed:"))
async def candidate_feed_page(cb: CallbackQuery):
    page = int(cb.data.split(":")[2])

    async with get_db() as session:
        cand = await _get_candidate(session, cb.from_user.id)
        if not cand:
            await cb.message.answer("Сначала зарегистрируйтесь как соискатель.")
            await cb.answer()
            return

        items, has_prev, has_next = await _get_feed(session, cand.id, page)
        if not items:
            await cb.message.answer("Больше вакансий нет.", reply_markup=candidate_menu())
            await cb.answer()
            return

        v = items[0]
        await cb.message.edit_text(
            _format_vacancy(v),
            reply_markup=candidate_vacancy_feed_kb(str(v.id), page, has_prev, has_next),
            parse_mode="HTML",
        )
        await cb.answer()


@router.callback_query(F.data.startswith("c:like:"))
async def candidate_like(cb: CallbackQuery):
    vacancy_id = cb.data.split(":")[2]

    async with get_db() as session:
        cand = await _get_candidate(session, cb.from_user.id)
        if not cand:
            await cb.answer("Сначала регистрация кандидата", show_alert=True)
            return

        session.add(Reaction(candidate_id=cand.id, vacancy_id=vacancy_id, value="like"))
        await session.commit()

    await cb.answer("👍 Сохранено в избранное", show_alert=False)


@router.callback_query(F.data.startswith("c:dislike:"))
async def candidate_dislike(cb: CallbackQuery):
    vacancy_id = cb.data.split(":")[2]

    async with get_db() as session:
        cand = await _get_candidate(session, cb.from_user.id)
        if not cand:
            await cb.answer("Сначала регистрация кандидата", show_alert=True)
            return

        session.add(Reaction(candidate_id=cand.id, vacancy_id=vacancy_id, value="dislike"))
        await session.commit()

    await cb.answer("👎", show_alert=False)


@router.callback_query(F.data == "c:menu")
async def candidate_back_menu(cb: CallbackQuery):
    await cb.message.answer("Главное меню", reply_markup=candidate_menu())
    await cb.answer()