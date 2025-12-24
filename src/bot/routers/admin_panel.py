from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.infrastructure.db.session import get_db
from src.infrastructure.db.models import (
    User, Recruiter, RecruiterApplication, Vacancy, Candidate
)
from src.bot.keyboards.admin import (
    admin_main_menu,
    applications_list_keyboard,
    application_detail_keyboard,
    back_to_admin_menu,
    users_list_keyboard,
    user_detail_keyboard,
    confirm_delete_keyboard,
)
from src.bot.keyboards.role import role_keyboard

router = Router()


# ═══════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════

async def get_admin_stats(session: AsyncSession) -> dict:
    """Статистика для панели"""
    total_users_result = await session.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar() or 0

    total_recruiters_result = await session.execute(
        select(func.count(Recruiter.id)).where(Recruiter.is_approved == True)
    )
    total_recruiters = total_recruiters_result.scalar() or 0

    active_vacancies_result = await session.execute(
        select(func.count(Vacancy.id)).where(Vacancy.status == "open")
    )
    active_vacancies = active_vacancies_result.scalar() or 0

    pending_apps_result = await session.execute(
        select(func.count(RecruiterApplication.id))
        .where(RecruiterApplication.status == "pending")
    )
    pending_apps = pending_apps_result.scalar() or 0

    return {
        "total_users": total_users,
        "total_recruiters": total_recruiters,
        "active_vacancies": active_vacancies,
        "pending_applications": pending_apps,
    }


def format_admin_panel(stats: dict) -> str:
    """Форматирует текст панели"""
    return (
        "👮‍♂️ <b>Панель Администратора</b>\n\n"
        "📊 <b>Статистика сервиса:</b>\n"
        f"👥 Всего пользователей: <b>{stats['total_users']}</b>\n"
        f"👔 Рекрутеров: <b>{stats['total_recruiters']}</b>\n"
        f"💼 Активных вакансий: <b>{stats['active_vacancies']}</b>\n\n"
        "Выберите раздел управления:"
    )


# ═══════════════════════════════════════════════════════════
# ГЛАВНОЕ МЕНЮ
# ═══════════════════════════════════════════════════════════

@router.callback_query(F.data == "admin:back_main")
async def admin_back_to_main(callback: CallbackQuery):
    """Возврат в главное меню"""
    async with get_db() as session:
        stats = await get_admin_stats(session)

    await callback.message.edit_text(
        format_admin_panel(stats),
        reply_markup=admin_main_menu(stats["pending_applications"]),
        parse_mode="HTML"
    )
    await callback.answer()


# ═══════════════════════════════════════════════════════════
# ЗАЯВКИ РЕКРУТЕРОВ
# ═══════════════════════════════════════════════════════════

@router.callback_query(F.data == "admin:applications")
async def admin_applications_list(callback: CallbackQuery):
    """Список заявок"""
    async with get_db() as session:
        result = await session.execute(
            select(RecruiterApplication)
            .where(RecruiterApplication.status == "pending")
            .order_by(RecruiterApplication.created_at.desc())
        )
        applications = list(result.scalars().all())

    if not applications:
        await callback.message.edit_text(
            "📭 Нет заявок на рассмотрении",
            reply_markup=back_to_admin_menu()
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        f"📢 <b>Заявки рекрутеров</b>\n\n"
        f"Ожидают рассмотрения: <b>{len(applications)}</b>\n\n"
        "Выберите заявку:",
        reply_markup=applications_list_keyboard(applications),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:app:"))
async def admin_view_application(callback: CallbackQuery):
    """Просмотр заявки"""
    app_id = callback.data.split(":")[2]

    async with get_db() as session:
        result = await session.execute(
            select(RecruiterApplication)
            .where(RecruiterApplication.id == app_id)
        )
        application = result.scalar_one_or_none()

        if not application:
            await callback.answer("Заявка не найдена", show_alert=True)
            return

        company_name = application.company.name if application.company else "?"

        if application.recruiter and application.recruiter.user:
            user = application.recruiter.user
            username = f"@{user.username}" if user.username else "нет username"
            telegram_id = user.telegram_id
            contact_name = application.recruiter.full_name or "?"
            position = application.recruiter.position or "?"
        else:
            username = "?"
            telegram_id = "?"
            contact_name = "?"
            position = "?"

        text = (
            f"📋 <b>Проверка рекрутера #{application.application_number}</b>\n\n"
            f"🏢 <b>Компания:</b> {company_name}\n"
            f"👤 <b>Юзер:</b> {username} (ID: {telegram_id})\n"
            f"📞 <b>Контактное лицо:</b> {contact_name}\n"
            f"💼 <b>Должность:</b> {position}\n"
            f"📅 <b>Дата заявки:</b> {application.created_at.strftime('%d.%m.%Y %H:%M')}"
        )

        app_id_for_keyboard = application.id

    await callback.message.edit_text(
        text,
        reply_markup=application_detail_keyboard(app_id_for_keyboard),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:approve:"))
async def admin_approve_application(callback: CallbackQuery, bot: Bot):
    """Одобрить заявку"""
    app_id = callback.data.split(":")[2]
    user_tg_id = None

    async with get_db() as session:
        result = await session.execute(
            select(RecruiterApplication).where(RecruiterApplication.id == app_id)
        )
        application = result.scalar_one_or_none()

        if not application:
            await callback.answer("Заявка не найдена", show_alert=True)
            return

        application.status = "approved"
        application.reviewed_at = datetime.now()

        if application.recruiter:
            application.recruiter.is_approved = True

            if application.recruiter.user:
                user_tg_id = application.recruiter.user.telegram_id

        await session.commit()

    if user_tg_id:
        try:
            await bot.send_message(
                user_tg_id,
                "🎉 <b>Ваша заявка одобрена!</b>\n\n"
                "Теперь вы можете создавать вакансии.\n"
                "Напишите /start чтобы открыть меню.",
                parse_mode="HTML"
            )
        except (Exception,):
            pass

    await callback.answer("✅ Заявка одобрена!", show_alert=True)
    await admin_applications_list(callback)


@router.callback_query(F.data.startswith("admin:reject:"))
async def admin_reject_application(callback: CallbackQuery, bot: Bot):
    """Отклонить заявку"""
    app_id = callback.data.split(":")[2]
    user_tg_id = None

    async with get_db() as session:
        result = await session.execute(
            select(RecruiterApplication).where(RecruiterApplication.id == app_id)
        )
        application = result.scalar_one_or_none()

        if not application:
            await callback.answer("Заявка не найдена", show_alert=True)
            return

        application.status = "rejected"
        application.reviewed_at = datetime.now()

        if application.recruiter and application.recruiter.user:
            user_tg_id = application.recruiter.user.telegram_id

        await session.commit()

    if user_tg_id:
        try:
            await bot.send_message(
                user_tg_id,
                "😔 <b>К сожалению, ваша заявка отклонена.</b>\n\n"
                "Если считаете это ошибкой, свяжитесь с поддержкой.",
                parse_mode="HTML"
            )
        except (Exception,):
            pass

    await callback.answer("❌ Заявка отклонена", show_alert=True)
    await admin_applications_list(callback)


# ═══════════════════════════════════════════════════════════
# УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ
# ═══════════════════════════════════════════════════════════

@router.callback_query(F.data == "admin:users")
async def admin_users_list(callback: CallbackQuery):
    """Список пользователей"""
    async with get_db() as session:
        result = await session.execute(
            select(User).order_by(User.created_at.desc())
        )
        users = list(result.scalars().all())

    if not users:
        await callback.message.edit_text(
            "👥 Пользователей пока нет",
            reply_markup=back_to_admin_menu()
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        f"👥 <b>Пользователи</b>\n\n"
        f"Всего: <b>{len(users)}</b>\n\n"
        "Выберите пользователя:",
        reply_markup=users_list_keyboard(users, page=0),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:users_page:"))
async def admin_users_page(callback: CallbackQuery):
    """Пагинация пользователей"""
    page = int(callback.data.split(":")[2])

    async with get_db() as session:
        result = await session.execute(
            select(User).order_by(User.created_at.desc())
        )
        users = list(result.scalars().all())

    await callback.message.edit_text(
        f"👥 <b>Пользователи</b>\n\n"
        f"Всего: <b>{len(users)}</b>\n\n"
        "Выберите пользователя:",
        reply_markup=users_list_keyboard(users, page=page),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:user:"))
async def admin_view_user(callback: CallbackQuery):
    """Просмотр пользователя"""
    user_id = callback.data.split(":")[2]

    text = ""
    is_banned = False
    target_user_id = None

    async with get_db() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return

        extra_info = ""

        if user.role == "recruiter":
            res = await session.execute(
                select(Recruiter).where(Recruiter.user_id == user.id)
            )
            recruiter = res.scalar_one_or_none()
            if recruiter:
                status = "✅ Одобрен" if recruiter.is_approved else "⏳ На модерации"
                extra_info = (
                    f"\n\n<b>Данные рекрутера:</b>\n"
                    f"👤 ФИО: {recruiter.full_name or '—'}\n"
                    f"💼 Должность: {recruiter.position or '—'}\n"
                    f"📊 Статус: {status}"
                )

        elif user.role == "candidate":
            res = await session.execute(
                select(Candidate).where(Candidate.user_id == user.id)
            )
            candidate = res.scalar_one_or_none()
            if candidate:
                extra_info = (
                    f"\n\n<b>Данные кандидата:</b>\n"
                    f"👤 ФИО: {candidate.full_name or '—'}\n"
                    f"🎂 Возраст: {candidate.age or '—'}\n"
                    f"🛠 Навыки: {candidate.skills or '—'}"
                )

        is_banned = getattr(user, 'is_banned', False)
        ban_status = "🚫 Забанен" if is_banned else "✅ Активен"

        created_at_str = "—"
        if hasattr(user, 'created_at') and user.created_at:
            created_at_str = user.created_at.strftime('%d.%m.%Y %H:%M')

        role_names = {"candidate": "Соискатель", "recruiter": "Рекрутер", "admin": "Админ"}

        text = (
            f"👤 <b>Пользователь</b>\n\n"
            f"🆔 ID: <code>{user.telegram_id}</code>\n"
            f"📛 Username: @{user.username or '—'}\n"
            f"👔 Роль: {role_names.get(user.role, user.role)}\n"
            f"📊 Статус: {ban_status}\n"
            f"📅 Регистрация: {created_at_str}"
            f"{extra_info}"
        )

        target_user_id = user.id

    await callback.message.edit_text(
        text,
        reply_markup=user_detail_keyboard(target_user_id, is_banned),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:ban:"))
async def admin_ban_user(callback: CallbackQuery):
    """Забанить пользователя"""
    user_id = callback.data.split(":")[2]

    async with get_db() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return

        user.is_banned = True
        await session.commit()

    await callback.answer("🚫 Пользователь забанен", show_alert=True)
    await admin_view_user(callback)


@router.callback_query(F.data.startswith("admin:unban:"))
async def admin_unban_user(callback: CallbackQuery):
    """Разбанить пользователя"""
    user_id = callback.data.split(":")[2]

    async with get_db() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return

        user.is_banned = False
        await session.commit()

    await callback.answer("✅ Пользователь разбанен", show_alert=True)
    await admin_view_user(callback)


@router.callback_query(F.data.startswith("admin:delete_user:"))
async def admin_delete_user_confirm(callback: CallbackQuery):
    """Подтверждение удаления пользователя"""
    user_id = callback.data.split(":")[2]

    await callback.message.edit_text(
        "⚠️ <b>Вы уверены?</b>\n\n"
        "Пользователь будет полностью удалён из системы вместе со всеми данными.",
        reply_markup=confirm_delete_keyboard("user", user_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:confirm_delete:user:"))
async def admin_confirm_delete_user(callback: CallbackQuery):
    """Удаление пользователя"""
    user_id = callback.data.split(":")[3]

    async with get_db() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return

        await session.execute(delete(Candidate).where(Candidate.user_id == user.id))
        await session.execute(delete(Recruiter).where(Recruiter.user_id == user.id))
        await session.execute(delete(User).where(User.id == user.id))

        await session.commit()

    await callback.answer("🗑 Пользователь удалён", show_alert=True)
    await admin_users_list(callback)


# ═══════════════════════════════════════════════════════════
# УДАЛЕНИЕ ВАКАНСИЙ
# ═══════════════════════════════════════════════════════════

@router.callback_query(F.data == "admin:delete_vacancy")
async def admin_delete_vacancy_list(callback: CallbackQuery):
    """Список вакансий для удаления"""
    async with get_db() as session:
        result = await session.execute(
            select(Vacancy)
            .where(Vacancy.status == "open")
            .order_by(Vacancy.created_at.desc())
            .limit(20)
        )
        vacancies = list(result.scalars().all())

    if not vacancies:
        await callback.message.edit_text(
            "📭 Нет активных вакансий",
            reply_markup=back_to_admin_menu()
        )
        await callback.answer()
        return

    buttons = []
    for v in vacancies:
        company_name = v.company.name if v.company else "?"
        btn_text = f"{v.title} ({company_name})"
        if len(btn_text) > 45:
            btn_text = btn_text[:42] + "..."
        buttons.append([
            InlineKeyboardButton(
                text=btn_text,
                callback_data=f"admin:vacancy:{v.id}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(text="◀️ Назад", callback_data="admin:back_main")
    ])

    await callback.message.edit_text(
        f"🗑 <b>Удаление вакансий</b>\n\n"
        f"Активных вакансий: <b>{len(vacancies)}</b>\n\n"
        "Выберите вакансию:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:vacancy:"))
async def admin_view_vacancy(callback: CallbackQuery):
    """Просмотр вакансии"""
    vacancy_id = callback.data.split(":")[2]

    text = ""
    target_vacancy_id = None

    async with get_db() as session:
        result = await session.execute(
            select(Vacancy).where(Vacancy.id == vacancy_id)
        )
        vacancy = result.scalar_one_or_none()

        if not vacancy:
            await callback.answer("Вакансия не найдена", show_alert=True)
            return

        company_name = vacancy.company.name if vacancy.company else "?"

        recruiter_info = "?"
        if vacancy.recruiter and vacancy.recruiter.user:
            recruiter_info = f"@{vacancy.recruiter.user.username or vacancy.recruiter.user.telegram_id}"

        description = vacancy.description or ""
        if len(description) > 500:
            description = description[:500] + "..."

        text = (
            f"📄 <b>{vacancy.title}</b>\n\n"
            f"🏢 Компания: {company_name}\n"
            f"👤 Рекрутер: {recruiter_info}\n"
            f"📅 Создана: {vacancy.created_at.strftime('%d.%m.%Y')}\n\n"
            f"📝 <b>Описание:</b>\n{description}"
        )

        target_vacancy_id = vacancy.id

    await callback.message.edit_text(
        text,
        reply_markup=confirm_delete_keyboard("vacancy", target_vacancy_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:confirm_delete:vacancy:"))
async def admin_confirm_delete_vacancy(callback: CallbackQuery):
    """Удаление вакансии"""
    vacancy_id = callback.data.split(":")[3]

    async with get_db() as session:
        result = await session.execute(
            select(Vacancy).where(Vacancy.id == vacancy_id)
        )
        vacancy = result.scalar_one_or_none()

        if not vacancy:
            await callback.answer("Вакансия не найдена", show_alert=True)
            return

        await session.execute(delete(Vacancy).where(Vacancy.id == vacancy_id))
        await session.commit()

    await callback.answer("🗑 Вакансия удалена", show_alert=True)
    await admin_delete_vacancy_list(callback)


# ═══════════════════════════════════════════════════════════
# ВЫХОД
# ═══════════════════════════════════════════════════════════

@router.callback_query(F.data == "admin:exit")
async def admin_exit(callback: CallbackQuery):
    """Выход в режим пользователя"""
    await callback.message.edit_text(
        "Вы вышли из режима администратора.\n"
        "Выберите роль:",
        reply_markup=role_keyboard()
    )
    await callback.answer()