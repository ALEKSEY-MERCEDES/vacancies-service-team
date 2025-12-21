from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def recruiter_candidate_detail_kb(candidate_id: str, vacancy_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📞 Пригласить",
                    callback_data=f"invite:{candidate_id}:{vacancy_id}",
                ),
                InlineKeyboardButton(
                    text="❌ Отказать",
                    callback_data=f"reject_confirm:{candidate_id}:{vacancy_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔙 К списку",
                    callback_data=f"vacancy_responses:{vacancy_id}",
                )
            ],
        ]
    )
