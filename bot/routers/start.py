from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import select

from bot.keyboards.role import role_keyboard
from bot.keyboards.common import candidate_menu, recruiter_menu
from bot.keyboards.admin import admin_menu
from infrastructure.db.session import get_session
from infrastructure.db.models import User

router = Router()

@router.message(F.text == "/start")
async def start_cmd(message: Message, state: FSMContext):
    await state.clear()

    async for session in get_session():
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        if user:
            if user.role == "candidate":
                await message.answer("Главное меню", reply_markup=candidate_menu())
            elif user.role == "recruiter":
                await message.answer("Главное меню", reply_markup=recruiter_menu())
            elif user.role == "admin":
                await message.answer("Админ-панель", reply_markup=admin_menu())
            return

    await message.answer("Выберите роль:", reply_markup=role_keyboard())
