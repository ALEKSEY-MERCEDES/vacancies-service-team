from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
import uuid

from src.bot.states.candidate_apply import CandidateApply
from src.bot.utils.notify_recruiter import notify_recruiter_new_application
from src.infrastructure.db.session import get_db
from src.infrastructure.db.models import User, Candidate, Vacancy, Application
from src.bot.keyboards.common import candidate_menu

router = Router()


async def _get_candidate(session, tg_id: int) -> Candidate | None:
    res = await session.execute(
        select(Candidate)
        .join(User, User.id == Candidate.user_id)
        .where(User.telegram_id == tg_id)
    )
    return res.scalar_one_or_none()


@router.callback_query(F.data.startswith("c:apply:"))
async def start_apply(cb: CallbackQuery, state: FSMContext):
    """Начинаем FSM отклика — просим сообщение"""
    vacancy_id_str = cb.data.split(":")[2]

    try:
        vacancy_uuid = uuid.UUID(vacancy_id_str)
    except ValueError:
        await cb.answer("Некорректный id вакансии", show_alert=True)
        return

    async with get_db() as session:
        cand = await _get_candidate(session, cb.from_user.id)
        if not cand:
            await cb.message.answer("Сначала зарегистрируйтесь как соискатель.")
            await cb.answer()
            return

        vac_res = await session.execute(
            select(Vacancy).where(Vacancy.id == vacancy_uuid)
        )
        vacancy = vac_res.scalar_one_or_none()
        if not vacancy:
            await cb.answer("Вакансия не найдена", show_alert=True)
            return

        res = await session.execute(
            select(Application).where(
                Application.vacancy_id == vacancy.id,
                Application.candidate_id == cand.id
            )
        )
        if res.scalar_one_or_none():
            await cb.answer("Вы уже откликались на эту вакансию ✅", show_alert=True)
            return

    await state.set_state(CandidateApply.message)
    await state.update_data(vacancy_id=vacancy_id_str)

    await cb.message.answer(
        "✍️ <b>Напишите сопроводительное сообщение</b>\n\n"
        "Или отправьте <code>-</code> чтобы откликнуться без сообщения.",
        parse_mode="HTML"
    )
    await cb.answer()


@router.message(CandidateApply.message)
async def finish_apply(message: Message, state: FSMContext):
    """Завершаем отклик — сохраняем в БД"""
    data = await state.get_data()
    vacancy_id_str = data.get("vacancy_id")

    if not vacancy_id_str:
        await message.answer("Что-то пошло не так. Попробуйте /start")
        await state.clear()
        return

    try:
        vacancy_uuid = uuid.UUID(vacancy_id_str)
    except ValueError:
        await message.answer("Ошибка. Попробуйте /start")
        await state.clear()
        return

    user_message = message.text.strip() if message.text else None
    if user_message == "-":
        user_message = None

    # Данные для уведомления — заполняются внутри блока
    notify_data: dict | None = None

    async with get_db() as session:
        cand = await _get_candidate(session, message.from_user.id)
        if not cand:
            await message.answer("Сначала зарегистрируйтесь как соискатель.")
            await state.clear()
            return

        vac_res = await session.execute(
            select(Vacancy).where(Vacancy.id == vacancy_uuid)
        )
        vacancy = vac_res.scalar_one_or_none()
        if not vacancy:
            await message.answer("Вакансия не найдена.")
            await state.clear()
            return

        res = await session.execute(
            select(Application).where(
                Application.vacancy_id == vacancy.id,
                Application.candidate_id == cand.id
            )
        )
        if res.scalar_one_or_none():
            await message.answer("Вы уже откликались на эту вакансию ✅")
            await state.clear()
            return

        app = Application(
            candidate_id=cand.id,
            vacancy_id=vacancy.id,
            message=user_message,
            status="sent"
        )
        session.add(app)
        await session.commit()

        # Собираем данные для уведомления в словарь
        if vacancy.recruiter:
            notify_data = {
                "recruiter_id": vacancy.recruiter.id,
                "vacancy_id": vacancy.id,
                "candidate_name": cand.full_name or "Без имени",
            }

    # Уведомляем рекрутера после закрытия сессии
    if notify_data:
        await notify_recruiter_new_application(
            bot=message.bot,
            recruiter_id=notify_data["recruiter_id"],
            vacancy_id=notify_data["vacancy_id"],
            candidate_name=notify_data["candidate_name"],
        )

    await state.clear()

    if user_message:
        await message.answer(
            "✅ <b>Отклик отправлен!</b>\n\n"
            f"💬 Ваше сообщение: <i>{user_message[:100]}{'...' if len(user_message) > 100 else ''}</i>",
            parse_mode="HTML",
            reply_markup=candidate_menu()
        )
    else:
        await message.answer(
            "✅ <b>Отклик отправлен!</b>",
            parse_mode="HTML",
            reply_markup=candidate_menu()
        )