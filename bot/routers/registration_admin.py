from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select

from infrastructure.db.session import get_session
from infrastructure.db.models import User, AdminWhitelist  # таблица whitelist
from bot.keyboards.admin import admin_menu  # меню админа

router = Router()

@router.callback_query(F.data == "role_admin")
async def role_admin(callback: CallbackQuery):
    tg_id = callback.from_user.id

    async for session in get_session():
        # проверка whitelist
        res = await session.execute(
            select(AdminWhitelist).where(AdminWhitelist.telegram_id == tg_id)
        )
        allowed = res.scalar_one_or_none()
        if not allowed:
            await callback.message.answer("❌ Нет доступа: вы не добавлены в список админов.")
            return

        # записываем/обновляем пользователя
        res = await session.execute(select(User).where(User.telegram_id == tg_id))
        user = res.scalar_one_or_none()

        if user is None:
            user = User(telegram_id=tg_id, username=callback.from_user.username, role="admin")
            session.add(user)
        else:
            user.role = "admin"

        await session.commit()

    await callback.message.answer("✅ Админ-доступ подтверждён", reply_markup=admin_menu())
