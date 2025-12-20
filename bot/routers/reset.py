from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, delete

from infrastructure.db.session import get_session
from infrastructure.db.models import User, Candidate

router = Router()

@router.callback_query(F.data == "wipe_me")
async def wipe_me_cb(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    tg_id = callback.from_user.id

    async for session in get_session():
        res = await session.execute(select(User).where(User.telegram_id == tg_id))
        user = res.scalar_one_or_none()
        if user is None:
            await callback.message.answer("Тебя нет в базе. /start")
            await callback.answer()
            return

        await session.execute(delete(Candidate).where(Candidate.user_id == user.id))
        await session.execute(delete(User).where(User.id == user.id))
        await session.commit()

    await callback.message.answer("🗑 Всё удалено. Напиши /start")
    await callback.answer()
