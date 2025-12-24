from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def recruiter_pending_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Проверить статус", callback_data="r:check_status")],
            [InlineKeyboardButton(text="🏠 В меню", callback_data="r:menu")],
        ]
    )

def recruiter_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Создать вакансию", callback_data="r:create_vacancy")],
        [InlineKeyboardButton(text="📂 Мои вакансии", callback_data="r:my_vacancies")],
        [InlineKeyboardButton(text="🗄 Архив вакансий", callback_data="r:archive")],  # ✅ NEW
        [InlineKeyboardButton(text="📊 Статистика", callback_data="r:stats")],
        [InlineKeyboardButton(text="🔄 Начать заново", callback_data="wipe_me")],
    ])



def vacancy_preview_menu(vacancy_id: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Опубликовать", callback_data=f"recruiter_vacancy_publish:{vacancy_id}")
    kb.button(text="❌ Отменить", callback_data="recruiter_vacancy_cancel")
    kb.button(text="🔙 В кабинет", callback_data="r:menu")
    kb.adjust(1)
    return kb.as_markup()