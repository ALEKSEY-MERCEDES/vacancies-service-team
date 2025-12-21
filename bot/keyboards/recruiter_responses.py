from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def recruiter_responses_kb(applications: list[dict], vacancy_id: str):
    keyboard = []

    for app in applications:
        icon = "🟢" if app["status"] == "sent" else "⚪️"

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"{icon} {app['full_name']}, {app['age']} лет",
                    callback_data=f"candidate:{app['candidate_id']}:{vacancy_id}",
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data=f"vacancy:{vacancy_id}",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
