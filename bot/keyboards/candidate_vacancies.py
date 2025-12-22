from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def candidate_vacancy_feed_kb(vacancy_id: str, page: int, has_prev: bool, has_next: bool) -> InlineKeyboardMarkup:
    nav = []
    if has_prev:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"c:feed:{page-1}"))
    if has_next:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"c:feed:{page+1}"))

    keyboard = [
        [
            InlineKeyboardButton(text="✍️ Откликнуться", callback_data=f"c:apply:{vacancy_id}")
        ],
        [
            InlineKeyboardButton(text="👍", callback_data=f"c:like:{vacancy_id}"),
            InlineKeyboardButton(text="👎", callback_data=f"c:dislike:{vacancy_id}"),
        ],
    ]

    if nav:
        keyboard.append(nav)

    keyboard.append([InlineKeyboardButton(text="🔙 В меню", callback_data="c:menu")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
