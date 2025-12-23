from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.utils.callbacks import pack_uuid

STATUS_ICONS = {
    "sent": "🆕",
    "viewed": "👀",
    "invited": "📞",
    "rejected": "❌"
}

def recruiter_responses_kb(applications: list[dict], vacancy_id: str) -> InlineKeyboardMarkup:
    keyboard = []

    v_short = pack_uuid(str(vacancy_id))

    for app in applications:
        status = app.get("status", "sent")
        icon = STATUS_ICONS.get(status, "⚪️")
        c_short = pack_uuid(str(app.get("candidate_id")))

        row = [
            InlineKeyboardButton(
                text=f"{icon} {app.get('full_name','Без имени')}, {app.get('age','?')} лет",
                callback_data=f"cand:{c_short}:{v_short}",  # Для просмотра профиля кандидата
            )
        ]

        if status != "invited":
            row.append(
                InlineKeyboardButton(
                    text="📩 Invite",
                    callback_data=f"recruiter:application:{c_short}:invite:{v_short}"
                )
            )

        keyboard.append(row)

    keyboard.append(
        [
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data=f"recruiter:vacancy:{v_short}"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
