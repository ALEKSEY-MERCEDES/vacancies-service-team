from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def candidate_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Смотреть вакансии", callback_data="vacancies")],
            [InlineKeyboardButton(text="🛡 Админ", callback_data="role_admin")],
            [InlineKeyboardButton(text="🔄 Начать заново", callback_data="wipe_me")],
        ]
    )


def recruiter_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Создать вакансию", callback_data="create_vacancy")],
            [InlineKeyboardButton(text="🛡 Админ", callback_data="role_admin")],
            [InlineKeyboardButton(text="🔄 Начать заново", callback_data="wipe_me")],
        ]
    )
