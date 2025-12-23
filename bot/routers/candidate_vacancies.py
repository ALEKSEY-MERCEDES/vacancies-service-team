from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, and_
import uuid

from sqlalchemy.exc import IntegrityError
from bot.utils.notify_recruiter import notify_recruiter_new_application
from infrastructure.db.session import get_session
from infrastructure.db.models import User, Candidate, Vacancy, Company, Application, Reaction, CandidateCompanyBlock, RecruiterCompany
from bot.keyboards.candidate_vacancies import candidate_vacancy_feed_kb
from bot.keyboards.common import candidate_menu

router = Router()

PER_PAGE = 1  # показываем по одной вакансии (как в тиндер-стиле). Можно 5/10 — но лучше 1.


async def _get_candidate(session, tg_id: int) -> Candidate | None:
    res = await session.execute(
        select(Candidate)
        .join(User, User.id == Candidate.user_id)
        .where(User.telegram_id == tg_id)
    )
    return res.scalar_one_or_none()


async def _get_feed(session, candidate_id, page: int):
    """
    Достаём open вакансии, исключая заблокированные компании (CandidateCompanyBlock).
    """
    # компании, которые кандидат заблокировал
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
        .offset(page * PER_PAGE)
        .limit(PER_PAGE + 1)  # чтобы понять есть ли next
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
async def candidate_feed_start(cb: CallbackQuery, reply_markup=None):
    async for session in get_session():
        cand = await _get_candidate(session, cb.from_user.id)

        if not cand:
            await cb.message.answer("Сначала зарегистрируйтесь как соискатель через меню роли.")
            await cb.answer()
            return

        page = 0
        items, has_prev, has_next = await _get_feed(session, cand.id, page)

        if not items:
            await cb.message.answer("Пока нет доступных вакансий 😕",
                                    reply_markup=candidate_menu())

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

    async for session in get_session():
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


@router.callback_query(F.data.startswith("c:apply:"))
async def candidate_apply(cb: CallbackQuery):
    # callback_data скорее всего: c:apply:<vacancy_id>:<page>
    vacancy_id_str = cb.data.split(":")[2]

    try:
        vacancy_uuid = uuid.UUID(vacancy_id_str)
    except ValueError:
        await cb.answer("Некорректный id вакансии", show_alert=True)
        return

    async for session in get_session():
        cand = await _get_candidate(session, cb.from_user.id)
        if not cand:
            await cb.message.answer("Сначала зарегистрируйтесь как соискатель.")
            await cb.answer()
            return

        # 1) достаём вакансию (нужна для recruiter/company/title и т.д.)
        vac_res = await session.execute(
            select(Vacancy).where(Vacancy.id == vacancy_uuid)
        )
        vacancy = vac_res.scalar_one_or_none()
        if not vacancy:
            await cb.answer("Вакансия не найдена", show_alert=True)
            return

        # 2) проверим не откликался ли уже
        res = await session.execute(
            select(Application).where(
                Application.vacancy_id == vacancy.id,
                Application.candidate_id == cand.id
            )
        )
        existing = res.scalar_one_or_none()
        if existing:
            await cb.answer("Вы уже откликались на эту вакансию ✅", show_alert=True)
            return

        # 3) создаём отклик
        app = Application(candidate_id=cand.id, vacancy_id=vacancy.id, status="sent")
        session.add(app)
        await session.commit()

        # 4) уведомляем рекрутера (если он есть у вакансии)
        recruiter = vacancy.recruiter
        if recruiter:
            await notify_recruiter_new_application(
                bot=cb.bot,
                recruiter_id=recruiter.id,
                vacancy_id=vacancy.id,
                candidate_name=cand.full_name or "Без имени",
            )

    await cb.answer("Отклик отправлен ✅", show_alert=True)



@router.callback_query(F.data.startswith("c:like:"))
async def candidate_like(cb: CallbackQuery):
    vacancy_id = cb.data.split(":")[2]

    async for session in get_session():
        cand = await _get_candidate(session, cb.from_user.id)
        if not cand:
            await cb.answer("Сначала регистрация кандидата", show_alert=True)
            return

        session.add(Reaction(candidate_id=cand.id, vacancy_id=vacancy_id, value="like"))
        await session.commit()

    await cb.answer("👍", show_alert=False)


@router.callback_query(F.data.startswith("c:dislike:"))
async def candidate_dislike(cb: CallbackQuery):
    vacancy_id = cb.data.split(":")[2]

    async for session in get_session():
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
