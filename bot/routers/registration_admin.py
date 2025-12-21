from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, func

from infrastructure.db.session import get_session
from infrastructure.db.models import User, AdminWhitelist, Recruiter, Vacancy, RecruiterApplication
from bot.keyboards.admin import admin_main_menu

router = Router()


async def get_admin_stats(session) -> dict:
    """Собирает статистику для панели"""

    # Всего пользователей
    total_users = await session.execute(select(func.count(User.id)))
    total_users = total_users.scalar()

    # Одобренных рекрутеров
    total_recruiters = await session.execute(
        select(func.count(Recruiter.id)).where(Recruiter.is_approved == True)
    )
    total_recruiters = total_recruiters.scalar()

    # Активных вакансий
    active_vacancies = await session.execute(
        select(func.count(Vacancy.id)).where(Vacancy.status == "open")
    )
    active_vacancies = active_vacancies.scalar()

    # Заявок на рассмотрении
    pending_apps = await session.execute(
        select(func.count(RecruiterApplication.id))
        .where(RecruiterApplication.status == "pending")
    )
    pending_apps = pending_apps.scalar()

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


@router.callback_query(F.data == "role_admin")
async def role_admin(callback: CallbackQuery):
    tg_id = callback.from_user.id

    async for session in get_session():
        # Проверка whitelist
        res = await session.execute(
            select(AdminWhitelist).where(AdminWhitelist.telegram_id == tg_id)
        )
        allowed = res.scalar_one_or_none()

        if not allowed:
            await callback.message.answer("❌ Нет доступа: вы не добавлены в список админов.")
            await callback.answer()
            return

        # Создаём/обновляем пользователя
        res = await session.execute(select(User).where(User.telegram_id == tg_id))
        user = res.scalar_one_or_none()

        if user is None:
            user = User(
                telegram_id=tg_id,
                username=callback.from_user.username,
                role="admin"
            )
            session.add(user)
        else:
            user.role = "admin"

        await session.commit()

        # Получаем статистику
        stats = await get_admin_stats(session)

    text = (
            "✅ Админ-доступ подтверждён\n\n" + format_admin_panel(stats)
    )

    await callback.message.answer(
        text,
        reply_markup=admin_main_menu(stats["pending_applications"]),
        parse_mode="HTML"
    )
    await callback.answer()