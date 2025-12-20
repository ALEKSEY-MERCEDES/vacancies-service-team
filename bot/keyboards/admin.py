from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📌 Модерация рекрутеров", callback_data="admin_recruiters")],
            [InlineKeyboardButton(text="🏢 Компании", callback_data="admin_companies")],
        ]
    )
