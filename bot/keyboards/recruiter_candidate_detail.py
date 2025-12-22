from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.utils.callbacks import pack_uuid

def recruiter_candidate_detail_kb(candidate_id: str, vacancy_id: str) -> InlineKeyboardMarkup:
    c = pack_uuid(str(candidate_id))
    v = pack_uuid(str(vacancy_id))

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📞 Пригласить", callback_data=f"invite:{c}:{v}"),
                InlineKeyboardButton(text="❌ Отказать", callback_data=f"reject_confirm:{c}:{v}"),
            ],
            [
                InlineKeyboardButton(
                    text="🔙 К списку",
                    callback_data=f"recruiter:vacancy:{v}:responses"   # ✅ ТОЛЬКО v_short
                )
            ],
        ]
    )
