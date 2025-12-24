from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def role_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👤 Соискатель", callback_data="role_candidate")],
            [InlineKeyboardButton(text="💼 Рекрутер", callback_data="role_recruiter")],
            [InlineKeyboardButton(text="🛡 Админ", callback_data="role_admin")],
        ]
    )