from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def recruiter_pending_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Проверить статус", callback_data="r:check_status")],
            [InlineKeyboardButton(text="🏠 В меню", callback_data="r:go_menu")],
        ]
    )


def recruiter_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Создать вакансию", callback_data="r:create_vacancy")],
            [InlineKeyboardButton(text="📂 Мои вакансии", callback_data="r:my_vacancies")],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="r:stats")],
            [InlineKeyboardButton(text="🔄 Начать заново", callback_data="wipe_me")],
        ]
    )
