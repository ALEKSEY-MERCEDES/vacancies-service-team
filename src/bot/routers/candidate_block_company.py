from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select
import uuid

from src.infrastructure.db.session import get_db
from src.infrastructure.db.models import User, Candidate, Vacancy, CandidateCompanyBlock
from src.bot.keyboards.candidate_vacancies import candidate_vacancy_feed_kb
from src.bot.keyboards.common import candidate_menu

router = Router()


async def _get_candidate(session, tg_id: int) -> Candidate | None:
    res = await session.execute(
        select(Candidate)
        .join(User, User.id == Candidate.user_id)
        .where(User.telegram_id == tg_id)
    )
    return res.scalar_one_or_none()


async def _get_feed(session, candidate_id, page: int):
    """Достаём вакансии, исключая заблокированные компании"""
    blocked_company_ids = select(CandidateCompanyBlock.company_id).where(
        CandidateCompanyBlock.candidate_id == candidate_id
    )

    q = (
        select(Vacancy)
        .where(
            Vacancy.status == "open",
            Vacancy.company_id.not_in(blocked_company_ids),
        )
        .order_by(Vacancy.created_at.desc())
        .offset(page)
        .limit(2)
    )

    res = await session.execute(q)
    items = list(res.scalars().all())

    has_next = len(items) > 1
    items = items[:1]
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


@router.callback_query(F.data.startswith("c:block_company:"))
async def block_company(cb: CallbackQuery):
    """Блокируем компанию и показываем следующую вакансию"""
    parts = cb.data.split(":")
    vacancy_id_str = parts[2]
    page = int(parts[3]) if len(parts) > 3 else 0

    try:
        vacancy_uuid = uuid.UUID(vacancy_id_str)
    except ValueError:
        await cb.answer("Ошибка", show_alert=True)
        return

    async with get_db() as session:
        cand = await _get_candidate(session, cb.from_user.id)
        if not cand:
            await cb.answer("Сначала зарегистрируйтесь", show_alert=True)
            return

        # Находим вакансию чтобы узнать company_id
        vac_res = await session.execute(
            select(Vacancy).where(Vacancy.id == vacancy_uuid)
        )
        vacancy = vac_res.scalar_one_or_none()
        if not vacancy:
            await cb.answer("Вакансия не найдена", show_alert=True)
            return

        company_id = vacancy.company_id
        company_name = vacancy.company.name if vacancy.company else "компанию"

        # Проверяем, не заблокирована ли уже
        existing = await session.execute(
            select(CandidateCompanyBlock).where(
                CandidateCompanyBlock.candidate_id == cand.id,
                CandidateCompanyBlock.company_id == company_id
            )
        )
        if not existing.scalar_one_or_none():
            block = CandidateCompanyBlock(
                candidate_id=cand.id,
                company_id=company_id
            )
            session.add(block)
            await session.commit()

        # Показываем следующую вакансию
        items, has_prev, has_next = await _get_feed(session, cand.id, page)

        # Отправляем ответ ВНУТРИ блока async with
        await cb.answer(f"🚫 {company_name} скрыта", show_alert=True)

        if not items:
            await cb.message.edit_text(
                "📭 Больше вакансий нет",
                reply_markup=candidate_menu()
            )
            return

        v = items[0]
        await cb.message.edit_text(
            _format_vacancy(v),
            reply_markup=candidate_vacancy_feed_kb(str(v.id), page, has_prev, has_next),
            parse_mode="HTML",
        )