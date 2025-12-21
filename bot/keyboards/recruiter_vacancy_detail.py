from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def recruiter_vacancy_detail_kb(vacancy_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📩 Смотреть отклики",
                    callback_data=f"vacancy_responses:{vacancy_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📥 В архив",
                    callback_data=f"vacancy_close:{vacancy_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="recruiter_vacancies",
                )
            ],
        ]
    )
