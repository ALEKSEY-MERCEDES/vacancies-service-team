from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def recruiter_stats_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 В кабинет", callback_data="r:menu")],
        ]
    )
