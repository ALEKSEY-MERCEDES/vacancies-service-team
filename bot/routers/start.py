from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import select

from bot.keyboards.role import role_keyboard
from bot.keyboards.common import candidate_menu, recruiter_menu
from bot.keyboards.recruiter import recruiter_main_menu, recruiter_pending_menu
from bot.utils.recruiter_access import get_recruiter_bundle

from infrastructure.db.session import get_session
from infrastructure.db.models import User
from bot.keyboards.admin import admin_menu
router = Router()


@router.message(F.text == "/start")
async def start_cmd(message: Message, state: FSMContext):
    await state.clear()

    async for session in get_session():
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        if not user:
            await message.answer("Выберите роль:", reply_markup=role_keyboard())
            return

        if user.role == "candidate":
            await message.answer("Главное меню", reply_markup=candidate_menu())
            return

        if user.role == "admin":
            await message.answer("Админ меню", reply_markup=admin_menu())
            return

        if user.role == "recruiter":
            _, recruiter, company = await get_recruiter_bundle(session, message.from_user.id)

            if not recruiter:
                # странный случай: роль recruiter есть, а recruiter записи нет
                await message.answer("Похоже, регистрация не завершена. Выберите роль заново.", reply_markup=role_keyboard())
                return

            if recruiter.status != "approved":
                await message.answer(
                    "⏳ Ваша заявка на модерации. Доступ откроется после подтверждения.",
                    reply_markup=recruiter_pending_menu(),
                )
                return

            company_name = company.name if company else "—"
            await message.answer(
                f"💼 Кабинет рекрутера\n\nКомпания: {company_name}\nСтатус: ✅ Подтвержден",
                reply_markup=recruiter_main_menu(),
            )
            return

    await message.answer("Выберите роль:", reply_markup=role_keyboard())
