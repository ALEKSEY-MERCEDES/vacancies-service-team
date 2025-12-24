from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def recruiter_vacancy_detail_kb(v_short: str, status: str = "open") -> InlineKeyboardMarkup:
    buttons = []

    buttons.append([
        InlineKeyboardButton(
            text="📩 Смотреть отклики",
            callback_data=f"recruiter:vacancy:{v_short}:responses",
        )
    ])

    if status == "open":
        buttons.append([
            InlineKeyboardButton(
                text="📥 В архив",
                callback_data=f"recruiter:vacancy:{v_short}:close",
            )
        ])
    else:
        buttons.append([
            InlineKeyboardButton(
                text="♻️ Переоткрыть",
                callback_data=f"recruiter:vacancy:{v_short}:reopen",
            )
        ])

    buttons.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="r:my_vacancies")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)