from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def recruiter_vacancies_kb(vacancies: list[dict]) -> InlineKeyboardMarkup:
    keyboard = []

    for v in vacancies:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"💼 {v['title']}  📩 {v['applications_count']}",
                    callback_data=f"vacancy:{v['id']}",
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="recruiter_main",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
