from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import uuid


def admin_main_menu(pending_count: int = 0) -> InlineKeyboardMarkup:
    """Главное меню админа с счётчиком заявок"""

    if pending_count > 0:
        applications_text = f"📢 Заявки рекрутеров ({pending_count})"
    else:
        applications_text = "📢 Заявки рекрутеров"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=applications_text, callback_data="admin:applications")],
            [InlineKeyboardButton(text="🔨 Управление пользователями", callback_data="admin:users")],
            [InlineKeyboardButton(text="🗑 Удалить вакансию", callback_data="admin:delete_vacancy")],
            [InlineKeyboardButton(text="🚪 Выйти в режим пользователя", callback_data="admin:exit")],
        ]
    )


def applications_list_keyboard(applications: list) -> InlineKeyboardMarkup:
    """Список заявок рекрутеров"""
    buttons = []

    for app in applications:
        company_name = app.company.name if app.company else "?"
        recruiter_name = app.recruiter.full_name if app.recruiter else "?"
        position = app.recruiter.position if app.recruiter else ""

        text = f"{company_name} - {recruiter_name} ({position})"
        if len(text) > 50:
            text = text[:47] + "..."

        buttons.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"admin:app:{app.id}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(text="◀️ Назад", callback_data="admin:back_main")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def application_detail_keyboard(application_id: uuid.UUID) -> InlineKeyboardMarkup:
    """Кнопки одобрить/отклонить"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Одобрить",
                    callback_data=f"admin:approve:{application_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Отклонить",
                    callback_data=f"admin:reject:{application_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="◀️ К списку заявок",
                    callback_data="admin:applications"
                )
            ],
        ]
    )


def back_to_admin_menu() -> InlineKeyboardMarkup:
    """Кнопка назад"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="admin:back_main")]
        ]
    )


def users_list_keyboard(users: list, page: int = 0, per_page: int = 8) -> InlineKeyboardMarkup:
    """Список пользователей с пагинацией"""
    buttons = []

    start = page * per_page
    end = start + per_page
    page_users = users[start:end]

    for user in page_users:
        role_emoji = {"candidate": "👤", "recruiter": "💼", "admin": "🛡"}.get(user.role, "❓")
        username = f"@{user.username}" if user.username else f"ID:{user.telegram_id}"
        text = f"{role_emoji} {username}"

        buttons.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"admin:user:{user.id}"
            )
        ])

    # Пагинация
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(text="◀️", callback_data=f"admin:users_page:{page - 1}")
        )
    if end < len(users):
        nav_buttons.append(
            InlineKeyboardButton(text="▶️", callback_data=f"admin:users_page:{page + 1}")
        )

    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append([
        InlineKeyboardButton(text="◀️ Назад", callback_data="admin:back_main")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def user_detail_keyboard(user_id: uuid.UUID, is_banned: bool = False) -> InlineKeyboardMarkup:
    """Детали пользователя"""
    buttons = []

    if is_banned:
        buttons.append([
            InlineKeyboardButton(text="🔓 Разбанить", callback_data=f"admin:unban:{user_id}")
        ])
    else:
        buttons.append([
            InlineKeyboardButton(text="🚫 Забанить", callback_data=f"admin:ban:{user_id}")
        ])

    buttons.append([
        InlineKeyboardButton(text="🗑 Удалить пользователя", callback_data=f"admin:delete_user:{user_id}")
    ])

    buttons.append([
        InlineKeyboardButton(text="◀️ К списку", callback_data="admin:users")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_delete_keyboard(entity_type: str, entity_id: uuid.UUID) -> InlineKeyboardMarkup:
    """Подтверждение удаления"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да, удалить",
                    callback_data=f"admin:confirm_delete:{entity_type}:{entity_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="admin:back_main"
                ),
            ],
        ]
    )