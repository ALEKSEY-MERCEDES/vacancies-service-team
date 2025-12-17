from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def candidate_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Смотреть вакансии", callback_data="vacancies")]
        ]
    )


def recruiter_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Создать вакансию", callback_data="create_vacancy")]
        ]
    )
