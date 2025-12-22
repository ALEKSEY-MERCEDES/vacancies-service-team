from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def recruiter_vacancies_kb(vacancies: list[dict]) -> InlineKeyboardMarkup:
    keyboard = []

    for v in vacancies:
        keyboard.append(
            [InlineKeyboardButton(
                text=f"💼 {v['title']}  📩 {v['applications_count']}",
                callback_data=f"recruiter:vacancy:{v['id']}",  # ✅ ВАЖНО
            )]
        )

    keyboard.append(
        [InlineKeyboardButton(text="🔙 Назад", callback_data="r:menu")]  # ✅ в кабинет
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
