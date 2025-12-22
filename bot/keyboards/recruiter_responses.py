from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.utils.callbacks import pack_uuid


def recruiter_responses_kb(applications: list[dict], vacancy_id: str) -> InlineKeyboardMarkup:
    keyboard = []

    v_short = pack_uuid(str(vacancy_id))  # ✅ коротко

    for app in applications:
        icon = "🟢" if app.get("status") == "sent" else "⚪️"
        c_short = pack_uuid(str(app.get("candidate_id")))

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"{icon} {app.get('full_name','Без имени')}, {app.get('age','?')} лет",
                    callback_data=f"cand:{c_short}:{v_short}",  # ✅ коротко + единый префикс
                )
            ]
        )

    # ✅ Назад в карточку вакансии (тоже через short)
    keyboard.append(
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"recruiter:vacancy:{v_short}")]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
