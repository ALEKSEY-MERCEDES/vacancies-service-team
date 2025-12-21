from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, update

from bot.states.recruiter_invite import RecruiterInvite
from infrastructure.db.session import get_session
from infrastructure.db.models import Candidate, User, Application

router = Router()


@router.callback_query(F.data.startswith("invite:"))
async def invite_start(callback: CallbackQuery, state: FSMContext):
    _, candidate_id, vacancy_id = callback.data.split(":")
    await state.update_data(candidate_id=candidate_id, vacancy_id=vacancy_id)
    await state.set_state(RecruiterInvite.message)
    await callback.message.answer("Напишите сообщение кандидату (оно уйдёт от имени бота):")


@router.message(RecruiterInvite.message, ~F.text.startswith("/"))
async def invite_send(message: Message, state: FSMContext):
    data = await state.get_data()
    candidate_id = data["candidate_id"]
    vacancy_id = data["vacancy_id"]
    invite_text = (message.text or "").strip()

    if not invite_text:
        await message.answer("Сообщение не может быть пустым. Напишите текст:")
        return

    async for session in get_session():
        # достать tg кандидата: Candidate.user_id -> User.telegram_id
        res = await session.execute(
            select(User.telegram_id)
            .select_from(Candidate)
            .join(User, User.id == Candidate.user_id)
            .where(Candidate.id == candidate_id)
        )
        candidate_tg = res.scalar_one_or_none()
        if not candidate_tg:
            await message.answer("❌ Не нашёл Telegram кандидата")
            await state.clear()
            return

        # обновить статус отклика
        await session.execute(
            update(Application)
            .where(
                Application.vacancy_id == vacancy_id,
                Application.candidate_id == candidate_id,
            )
            .values(status="invited", message=invite_text)
        )
        await session.commit()

    # отправка кандидату (важно: bot доступен через message.bot)
    await message.bot.send_message(
        chat_id=candidate_tg,
        text="✅ Вас пригласили на следующий этап!\n\n" + invite_text,
    )

    await state.clear()
    await message.answer("✅ Приглашение отправлено кандидату.")
