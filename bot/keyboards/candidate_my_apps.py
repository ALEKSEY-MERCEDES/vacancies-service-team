from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def candidate_my_apps_kb(items: list[dict], page: int, has_prev: bool, has_next: bool) -> InlineKeyboardMarkup:
    keyboard = []

    for it in items:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{it['status_icon']} {it['title']} — {it['company']}",
                callback_data=f"c:app:{it['app_id']}",
            )
        ])

    nav = []
    if has_prev:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"c:my_apps:{page-1}"))
    if has_next:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"c:my_apps:{page+1}"))
    if nav:
        keyboard.append(nav)

    keyboard.append([InlineKeyboardButton(text="🔙 В меню", callback_data="c:menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
