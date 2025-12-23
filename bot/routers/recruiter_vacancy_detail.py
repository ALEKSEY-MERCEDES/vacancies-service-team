from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select, func, update

from infrastructure.db.session import get_session
from infrastructure.db.models import Vacancy, Application, Candidate, User
from bot.keyboards.recruiter_vacancy_detail import recruiter_vacancy_detail_kb
from bot.keyboards.recruiter_responses import recruiter_responses_kb
from bot.utils.callbacks import unpack_uuid

router = Router()


def safe_uuid(token: str) -> str:
    if len(token) >= 32 and "-" in token:
        return token
    return unpack_uuid(token)


# =========================================================
# FSM для Invite
# =========================================================
class InviteCandidate(StatesGroup):
    waiting_for_text = State()


# =========================================================
# Рисуем отклики
# =========================================================
async def render_responses(cb: CallbackQuery, session, vacancy_id: str, edit: bool = False, only_new: bool = False):
    result = await session.execute(
        select(Application, Candidate)
        .join(Candidate, Candidate.id == Application.candidate_id)
        .where(Application.vacancy_id == vacancy_id)
        .order_by(Application.created_at.desc())
    )

    applications = result.all()

    if only_new:
        applications_ui = [
            {
                "candidate_id": str(candidate.id),
                "full_name": candidate.full_name or "Без имени",
                "age": candidate.age or "?",
                "status": app.status,
            }
            for app, candidate in applications
            if app.status == "sent"
        ]
    else:
        applications_ui = [
            {
                "candidate_id": str(candidate.id),
                "full_name": candidate.full_name or "Без имени",
                "age": candidate.age or "?",
                "status": app.status,
            }
            for app, candidate in applications
        ]

    if not applications_ui:
        text = "📭 Пока нет откликов на эту вакансию."
        if edit:
            await cb.message.edit_text(text)
        else:
            await cb.message.answer(text)
        return

    text = f"📩 Отклики на вакансию\n\nВсего кандидатов: {len(applications_ui)}"

    kb = recruiter_responses_kb(applications_ui, vacancy_id)

    filter_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🆕 Только новые",
                    callback_data=f"recruiter:vacancy:{vacancy_id}:responses:filter:new",
                ),
                InlineKeyboardButton(
                    text="📋 Все",
                    callback_data=f"recruiter:vacancy:{vacancy_id}:responses:filter:all",
                ),
            ]
        ]
    )
    kb.inline_keyboard = filter_kb.inline_keyboard + kb.inline_keyboard

    if edit:
        await cb.message.edit_text(text, reply_markup=kb)
    else:
        await cb.message.answer(text, reply_markup=kb)


# =========================================================
# Карточка вакансии
# =========================================================
@router.callback_query(
    F.data.startswith("recruiter:vacancy:")
    & ~F.data.endswith(":responses")
    & ~F.data.endswith(":close")
    & ~F.data.endswith(":reopen")
)
async def recruiter_vacancy_detail(callback: CallbackQuery):
    v_token = callback.data.split(":")[2]
    vacancy_id = safe_uuid(v_token)

    async with get_session() as session:
        vacancy_res = await session.execute(
            select(Vacancy).where(Vacancy.id == vacancy_id)
        )
        vacancy = vacancy_res.scalar_one_or_none()

        if not vacancy:
            await callback.message.answer("❌ Вакансия не найдена")
            await callback.answer()
            return

        apps_res = await session.execute(
            select(func.count(Application.id)).where(
                Application.vacancy_id == vacancy.id
            )
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


# =========================================================
# Отклики
# =========================================================
@router.callback_query(
    F.data.startswith("recruiter:vacancy:") & F.data.endswith(":responses")
)
async def recruiter_vacancy_responses(callback: CallbackQuery):
    v_token = callback.data.split(":")[2]
    vacancy_id = safe_uuid(v_token)

    async with get_session() as session:
        await render_responses(callback, session, vacancy_id)

    await callback.answer()


# =========================================================
# Фильтр
# =========================================================
@router.callback_query(
    F.data.startswith("recruiter:vacancy:")
    & F.data.contains(":responses:filter:")
)
async def recruiter_responses_filter(cb: CallbackQuery):
    parts = cb.data.split(":")
    v_token = parts[2]
    filter_type = parts[-1]
    vacancy_id = safe_uuid(v_token)
    only_new = filter_type == "new"

    async with get_session() as session:
        await render_responses(cb, session, vacancy_id, edit=True, only_new=only_new)

    await cb.answer()


# =========================================================
# Invite кандидата
# =========================================================
@router.callback_query(
    F.data.startswith("recruiter:application:") & F.data.contains(":invite")
)
async def recruiter_invite_start(cb: CallbackQuery, state: FSMContext):
    parts = cb.data.split(":")
    candidate_id = parts[2]
    vacancy_id = parts[4] if len(parts) > 4 else None

    await state.update_data(candidate_id=candidate_id, vacancy_id=vacancy_id)
    await cb.message.answer("📝 Напишите сообщение кандидату:")
    await InviteCandidate.waiting_for_text.set()  # type: ignore
    await cb.answer()


@router.message(InviteCandidate.waiting_for_text)
async def recruiter_invite_send(message: Message, state: FSMContext):
    data = await state.get_data()
    candidate_id = data["candidate_id"]
    vacancy_id = data.get("vacancy_id")
    text_to_candidate = message.text

    async with get_session() as session:
        await session.execute(
            update(Application)
            .where(Application.candidate_id == candidate_id)
            .values(status="invited")
        )
        await session.commit()

        result = await session.execute(
            select(Candidate, User)
            .join(User, User.id == Candidate.user_id)
            .where(Candidate.id == candidate_id)
        )
        row = result.first()

        vacancy_res = await session.execute(
            select(Vacancy).where(Vacancy.id == vacancy_id)
        )
        vacancy = vacancy_res.scalar_one_or_none()

    if row:
        candidate, user = row
        if user.telegram_id:
            await message.bot.send_message(
                chat_id=user.telegram_id,
                text=f"{text_to_candidate}\n\n💼 Вакансия: {vacancy.title if vacancy else 'неизвестна'}",
            )

    cb_edit = CallbackQuery(
        id=str(message.message_id),
        from_user=message.from_user,
        chat_instance="0",
        message=message,
        data=f"recruiter:vacancy:{vacancy_id}:responses",
    )

    async with get_session() as session:
        await render_responses(cb_edit, session, vacancy_id, edit=True)

    await state.clear()


# =========================================================
# Закрыть / открыть вакансию
# =========================================================
@router.callback_query(
    F.data.startswith("recruiter:vacancy:") & F.data.endswith(":close")
)
async def recruiter_vacancy_close(callback: CallbackQuery):
    v_token = callback.data.split(":")[2]
    vacancy_id = safe_uuid(v_token)

    async with get_session() as session:
        await session.execute(
            update(Vacancy).where(Vacancy.id == vacancy_id).values(status="closed")
        )
        await session.commit()

    await callback.message.answer("📥 Вакансия закрыта (в архив).")
    await callback.answer()


@router.callback_query(
    F.data.startswith("recruiter:vacancy:") & F.data.endswith(":reopen")
)
async def recruiter_vacancy_reopen(callback: CallbackQuery):
    v_token = callback.data.split(":")[2]
    vacancy_id = safe_uuid(v_token)

    async with get_session() as session:
        await session.execute(
            update(Vacancy).where(Vacancy.id == vacancy_id).values(status="open")
        )
        await session.commit()

    await callback.message.answer("♻️ Вакансия снова активна (открыта).")
    await callback.answer()
