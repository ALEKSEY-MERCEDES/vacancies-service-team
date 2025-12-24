from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.bot.utils.callbacks import pack_uuid

def recruiter_vacancies_kb(vacancies: list[dict]) -> InlineKeyboardMarkup:
    keyboard = []

    for v in vacancies:
        v_short = pack_uuid(v["id"])
        keyboard.append(
            [InlineKeyboardButton(
                text=f"💼 {v['title']}  📩 {v['applications_count']}",
                callback_data=f"recruiter:vacancy:{v_short}",
            )]
        )

    keyboard.append(
        [InlineKeyboardButton(text="🔙 Назад", callback_data="r:menu")]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)