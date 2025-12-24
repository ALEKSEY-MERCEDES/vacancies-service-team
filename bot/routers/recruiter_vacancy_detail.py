from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, func, update

from infrastructure.db.session import get_session
from infrastructure.db.models import Vacancy, Application, Candidate
from bot.keyboards.recruiter_vacancy_detail import recruiter_vacancy_detail_kb
from bot.keyboards.recruiter_responses import recruiter_responses_kb
from bot.utils.callbacks import unpack_uuid

router = Router()


def safe_uuid(token: str) -> str:
    if len(token) >= 32 and "-" in token:
        return token
    return unpack_uuid(token)


async def render_responses(cb: CallbackQuery, session, vacancy_id: str, edit: bool = False):
    result = await session.execute(
        select(Application, Candidate)
        .join(Candidate, Candidate.id == Application.candidate_id)
        .where(Application.vacancy_id == vacancy_id)
        .order_by(Application.created_at.desc())
    )

    applications_ui = []
    for app, candidate in result.all():
        applications_ui.append(
            {
                "candidate_id": str(candidate.id),
                "full_name": candidate.full_name or "Без имени",
                "age": candidate.age or "?",
                "status": app.status,
            }
        )

    if not applications_ui:
        text = "📭 Пока нет откликов на эту вакансию."
        if edit:
            await cb.message.edit_text(text)
        else:
            await cb.message.answer(text)
        return

    text = (
        f"📩 Отклики на вакансию\n\n"
        f"Всего кандидатов: {len(applications_ui)}"
    )

    kb = recruiter_responses_kb(applications_ui, vacancy_id)

    if edit:
        await cb.message.edit_text(text, reply_markup=kb)
    else:
        await cb.message.answer(text, reply_markup=kb)


@router.callback_query(
    F.data.startswith("recruiter:vacancy:")
    & ~F.data.endswith(":responses")
    & ~F.data.endswith(":close")
    & ~F.data.endswith(":reopen")
)
async def recruiter_vacancy_detail(callback: CallbackQuery):
    v_token = callback.data.split(":")[2]
    vacancy_id = safe_uuid(v_token)

    async for session in get_session():
        vacancy_res = await session.execute(
            select(Vacancy).where(Vacancy.id == vacancy_id)
        )
        vacancy = vacancy_res.scalar_one_or_none()

        if not vacancy:
            await callback.message.answer("❌ Вакансия не найдена")
            await callback.answer()
            return

        apps_res = await session.execute(
            select(func.count(Application.id))
            .where(Application.vacancy_id == vacancy.id)
        )
        applications_count = apps_res.scalar() or 0

    status_text = "🟢 Активна" if vacancy.status == "open" else "🔴 Закрыта"

    await callback.message.answer(
        f"💼 {vacancy.title}\n"
        f"Статус: {status_text}\n\n"
        f"Всего откликов: {applications_count}\n"
        f"Опубликована: {vacancy.created_at:%d.%m.%Y}",
        reply_markup=recruiter_vacancy_detail_kb(v_token, vacancy.status),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("recruiter:vacancy:") & F.data.endswith(":responses"))
async def recruiter_vacancy_responses(callback: CallbackQuery):
    v_token = callback.data.split(":")[2]
    vacancy_id = safe_uuid(v_token)

    async for session in get_session():
        await render_responses(callback, session, vacancy_id, edit=False)

    await callback.answer()


@router.callback_query(F.data.startswith("recruiter:vacancy:") & F.data.endswith(":close"))
async def recruiter_vacancy_close(callback: CallbackQuery):
    v_token = callback.data.split(":")[2]
    vacancy_id = safe_uuid(v_token)

    async for session in get_session():
        await session.execute(
            update(Vacancy)
            .where(Vacancy.id == vacancy_id)
            .values(status="closed")
        )
        await session.commit()

    await callback.message.answer("📥 Вакансия закрыта (в архив).")
    await callback.answer()


@router.callback_query(F.data.startswith("recruiter:vacancy:") & F.data.endswith(":reopen"))
async def recruiter_vacancy_reopen(callback: CallbackQuery):
    v_token = callback.data.split(":")[2]
    vacancy_id = safe_uuid(v_token)

    async for session in get_session():
        await session.execute(
            update(Vacancy)
            .where(Vacancy.id == vacancy_id)
            .values(status="open")
        )
        await session.commit()

    await callback.message.answer("♻️ Вакансия снова активна (открыта).")
    await callback.answer()