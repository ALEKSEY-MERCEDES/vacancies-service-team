from aiogram import Router, F
from aiogram.types import CallbackQuery

from infrastructure.db.session import get_session
from bot.utils.recruiter_access import get_recruiter_bundle
from bot.keyboards.recruiter import recruiter_main_menu, recruiter_pending_menu
from bot.keyboards.role import role_keyboard

router = Router()


@router.callback_query(F.data == "r:check_status")
async def r_check_status(cb: CallbackQuery):
    async for session in get_session():
        user, recruiter, company = await get_recruiter_bundle(session, cb.from_user.id)

        if not user or not recruiter:
            await cb.message.answer("Сначала выберите роль.", reply_markup=role_keyboard())
            await cb.answer()
            return

        # ИСПРАВЛЕНО: было recruiter.status, стало recruiter.is_approved
        if not recruiter.is_approved:
            await cb.message.answer(
                "⏳ Вы всё ещё на модерации. Админ скоро проверит данные.",
                reply_markup=recruiter_pending_menu()
            )
            await cb.answer()
            return

        company_name = company.name if company else "—"
        await cb.message.answer(
            f"💼 Кабинет рекрутера\n\nКомпания: {company_name}\nСтатус: ✅ Подтвержден",
            reply_markup=recruiter_main_menu()
        )
        await cb.answer()


@router.callback_query(F.data == "r:go_menu")
async def r_go_menu(cb: CallbackQuery):
    await cb.message.answer("Выберите роль:", reply_markup=role_keyboard())
    await cb.answer()