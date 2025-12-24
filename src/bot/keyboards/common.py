from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def candidate_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Смотреть вакансии", callback_data="vacancies")],
            [InlineKeyboardButton(text="📨 Мои отклики", callback_data="c:my_apps")],
            [InlineKeyboardButton(text="⭐ Сохранённые", callback_data="c:saved")],
            [InlineKeyboardButton(text="🔄 Начать заново", callback_data="wipe_me")],
        ]
    )

def recruiter_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Создать вакансию", callback_data="create_vacancy")],
            [InlineKeyboardButton(text="📂 Мои вакансии", callback_data="my_vacancies")],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="recruiter_stats")],
            [InlineKeyboardButton(text="🔄 Начать заново", callback_data="wipe_me")],
        ]
    )