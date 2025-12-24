from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def candidate_saved_kb(items: list[dict], page: int, has_prev: bool, has_next: bool) -> InlineKeyboardMarkup:
    """Список сохранённых вакансий"""
    keyboard = []

    for it in items:
        keyboard.append([
            InlineKeyboardButton(
                text=f"⭐ {it['title']} — {it['company']}",
                callback_data=f"c:saved_detail:{it['vacancy_id']}",
            )
        ])

    # Пагинация
    nav = []
    if has_prev:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"c:saved:{page - 1}"))
    if has_next:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"c:saved:{page + 1}"))
    if nav:
        keyboard.append(nav)

    keyboard.append([InlineKeyboardButton(text="🔙 В меню", callback_data="c:menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def candidate_saved_detail_kb(vacancy_id: str) -> InlineKeyboardMarkup:
    """Детали сохранённой вакансии"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✍️ Откликнуться", callback_data=f"c:apply:{vacancy_id}")],
            [InlineKeyboardButton(text="💔 Убрать из сохранённых", callback_data=f"c:unsave:{vacancy_id}")],
            [InlineKeyboardButton(text="🔙 К сохранённым", callback_data="c:saved:0")],
        ]
    )