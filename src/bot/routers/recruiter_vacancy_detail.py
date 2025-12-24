from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select, func, update

from src.infrastructure.db.session import get_db
from src.infrastructure.db.models import Vacancy, Application, Candidate, User
from src.bot.keyboards.recruiter_vacancy_detail import recruiter_vacancy_detail_kb
from src.bot.keyboards.recruiter_responses import recruiter_responses_kb
from src.bot.utils.callbacks import unpack_uuid, pack_uuid

router = Router()


def safe_uuid(token: str) -> str:
    """Принимает либо v_short (упакованный), либо полный UUID."""
    if len(token) >= 32 and "-" in token:
        return token
    return unpack_uuid(token)


class InviteCandidate(StatesGroup):
    waiting_for_text = State()


async def render_responses(
    cb: CallbackQuery,
    session,
    vacancy_id: str,
    edit: bool = False,
    only_new: bool = False,
):
    result = await session.execute(
        select(Application, Candidate)
        .join(Candidate, Candidate.id == Application.candidate_id)
        .where(Application.vacancy_id == vacancy_id)
        .order_by(Application.created_at.desc())
    )

    rows = result.all()

    if only_new:
        rows = [row for row in rows if row[0].status == "sent"]

    applications_ui: list[dict] = []
    for app, candidate in rows:
        applications_ui.append(
            {
                "candidate_id": str(candidate.id),
                "full_name": candidate.full_name or "Без имени",
                "age": candidate.age or "?",
                "status": app.status,
            }
        )

    v_short = pack_uuid(str(vacancy_id))

    if not applications_ui:
        text = "📭 Пока нет откликов на эту вакансию."
        back_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data=f"recruiter:vacancy:{v_short}")]
            ]
        )
        if edit:
            await cb.message.edit_text(text, reply_markup=back_kb)
        else:
            await cb.message.answer(text, reply_markup=back_kb)
        return

    text = f"📩 Отклики на вакансию\n\nВсего кандидатов: {len(applications_ui)}"

    kb = recruiter_responses_kb(applications_ui, vacancy_id)

    filter_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🆕 Только новые",
                    callback_data=f"rf:n:{v_short}",
                ),
                InlineKeyboardButton(
                    text="📋 Все",
                    callback_data=f"rf:a:{v_short}",
                ),
            ]
        ]
    )
    kb.inline_keyboard = filter_kb.inline_keyboard + kb.inline_keyboard

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

    async with get_db() as session:
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


@router.callback_query(
    F.data.startswith("recruiter:vacancy:") & F.data.endswith(":responses")
)
async def recruiter_vacancy_responses(callback: CallbackQuery):
    v_token = callback.data.split(":")[2]
    vacancy_id = safe_uuid(v_token)

    async with get_db() as session:
        await render_responses(callback, session, vacancy_id)
        await callback.answer()


@router.callback_query(F.data.startswith("rf:"))
async def recruiter_responses_filter(cb: CallbackQuery):
    _, mode, v_short = cb.data.split(":")
    vacancy_id = safe_uuid(v_short)
    only_new = mode == "n"

    async with get_db() as session:
        await render_responses(cb, session, vacancy_id, edit=True, only_new=only_new)
        await cb.answer()


@router.callback_query(F.data.startswith("inv:"))
async def recruiter_invite_start(cb: CallbackQuery, state: FSMContext):
    _, c_short, v_short = cb.data.split(":")
    candidate_id = safe_uuid(c_short)
    vacancy_id = safe_uuid(v_short)

    await state.update_data(candidate_id=candidate_id, vacancy_id=vacancy_id)
    await cb.message.answer("📝 Напишите сообщение кандидату:")
    await state.set_state(InviteCandidate.waiting_for_text)
    await cb.answer()


@router.message(InviteCandidate.waiting_for_text)
async def recruiter_invite_send(message: Message, state: FSMContext):
    data = await state.get_data()
    candidate_id = data["candidate_id"]
    vacancy_id = data.get("vacancy_id")
    text_to_candidate = message.text or ""

    user_telegram_id = None
    vacancy_title = "неизвестна"

    async with get_db() as session:
        await session.execute(
            update(Application)
            .where(Application.candidate_id == candidate_id)
            .where(Application.vacancy_id == vacancy_id)
            .values(status="invited")
        )
        await session.commit()

        result = await session.execute(
            select(Candidate, User)
            .join(User, User.id == Candidate.user_id)
            .where(Candidate.id == candidate_id)
        )
        row = result.first()

        if row:
            candidate, user = row
            user_telegram_id = user.telegram_id

        vacancy_res = await session.execute(
            select(Vacancy).where(Vacancy.id == vacancy_id)
        )
        vacancy = vacancy_res.scalar_one_or_none()
        if vacancy:
            vacancy_title = vacancy.title

    if user_telegram_id:
        await message.bot.send_message(
            chat_id=user_telegram_id,
            text=f"{text_to_candidate}\n\n💼 Вакансия: {vacancy_title}",
        )

    await message.answer("✅ Приглашение отправлено!")
    await state.clear()


@router.callback_query(
    F.data.startswith("recruiter:vacancy:") & F.data.endswith(":close")
)
async def recruiter_vacancy_close(callback: CallbackQuery):
    v_token = callback.data.split(":")[2]
    vacancy_id = safe_uuid(v_token)

    async with get_db() as session:
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

    async with get_db() as session:
        await session.execute(
            update(Vacancy).where(Vacancy.id == vacancy_id).values(status="open")
        )
        await session.commit()

        await callback.message.answer("♻️ Вакансия снова активна (открыта).")
        await callback.answer()