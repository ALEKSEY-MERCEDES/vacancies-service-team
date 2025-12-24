from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def recruiter_reject_confirm_kb(candidate_id: str, vacancy_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да, отказать",
                    callback_data=f"reject:{candidate_id}:{vacancy_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Нет, вернуться",
                    callback_data=f"candidate:{candidate_id}:{vacancy_id}",
                )
            ],
        ]
    )