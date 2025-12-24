from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.bot.utils.callbacks import pack_uuid


def recruiter_archive_kb(vacancies: list[dict]) -> InlineKeyboardMarkup:
    keyboard = []

    for v in vacancies:
        v_short = pack_uuid(str(v["id"]))
        keyboard.append([
            InlineKeyboardButton(
                text=f"🗄 {v['title']}  📩 {v['applications_count']}",
                callback_data=f"recruiter:vacancy:{v_short}",  # ✅ открываем карточку
            )
        ])

    keyboard.append([InlineKeyboardButton(text="🔙 В кабинет", callback_data="r:menu")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)