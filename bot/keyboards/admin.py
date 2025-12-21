from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Одобрить рекрутера", callback_data="admin_approve_recruiters")],
            [InlineKeyboardButton(text="🏢 Компании", callback_data="admin_companies")],
            [InlineKeyboardButton(text="📄 Вакансии", callback_data="admin_vacancies")],
            [InlineKeyboardButton(text="🔄 Начать заново", callback_data="wipe_me")],
        ]
    )
