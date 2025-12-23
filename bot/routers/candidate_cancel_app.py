from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, delete
import uuid

from infrastructure.db.session import get_db
from infrastructure.db.models import User, Candidate, Application
from bot.keyboards.common import candidate_menu

router = Router()


async def _get_candidate(session, tg_id: int) -> Candidate | None:
    res = await session.execute(
        select(Candidate)
        .join(User, User.id == Candidate.user_id)
        .where(User.telegram_id == tg_id)
    )
    return res.scalar_one_or_none()


@router.callback_query(F.data.startswith("c:cancel_app_confirm:"))
async def cancel_app_confirm(cb: CallbackQuery):
    """Подтверждение отмены отклика"""
    app_id = cb.data.split(":")[2]

    await cb.message.answer(
        "⚠️ <b>Вы уверены?</b>\n\n"
        "Отклик будет удалён и рекрутер его больше не увидит.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Да, отменить",
                        callback_data=f"c:cancel_app:{app_id}"
                    ),
                    InlineKeyboardButton(
                        text="❌ Нет",
                        callback_data=f"c:app:{app_id}"
                    ),
                ]
            ]
        )
    )
    await cb.answer()


@router.callback_query(F.data.startswith("c:cancel_app:"))
async def cancel_app(cb: CallbackQuery):
    """Отмена отклика — удаляем из БД"""
    app_id = cb.data.split(":")[2]

    try:
        app_uuid = uuid.UUID(app_id)
    except ValueError:
        await cb.answer("Ошибка", show_alert=True)
        return

    async with get_db() as session:
        cand = await _get_candidate(session, cb.from_user.id)
        if not cand:
            await cb.answer("Ошибка", show_alert=True)
            return

        # Проверяем что отклик принадлежит этому кандидату
        res = await session.execute(
            select(Application)
            .where(Application.id == app_uuid)
            .where(Application.candidate_id == cand.id)
        )
        app = res.scalar_one_or_none()

        if not app:
            await cb.answer("Отклик не найден", show_alert=True)
            return

        # Удаляем
        await session.execute(
            delete(Application).where(Application.id == app_uuid)
        )
        await session.commit()

        await cb.answer("🗑 Отклик отменён", show_alert=True)
        await cb.message.answer(
            "✅ Отклик успешно отменён",
            reply_markup=candidate_menu()
        )