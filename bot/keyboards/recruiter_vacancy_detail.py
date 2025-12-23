from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def recruiter_vacancy_detail_kb(v_short: str) -> InlineKeyboardMarkup:
    """
    v_short — короткий id вакансии (pack_uuid(uuid)).
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📩 Смотреть отклики",
                    callback_data=f"recruiter:vacancy:{v_short}:responses",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📥 В архив",
                    callback_data=f"recruiter:vacancy:{v_short}:close",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="r:my_vacancies",
                )
            ],
        ]
    )