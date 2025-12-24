from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, delete, func as sql_func  # ← добавить sql_func

from src.bot.states.recruiter import RecruiterRegistration
from src.bot.keyboards.recruiter import recruiter_pending_menu

from src.infrastructure.db.session import get_session
from src.infrastructure.db.models import (
    User, Recruiter, Company, RecruiterCompany,
    RecruiterApplication  # ← добавить
)

router = Router()


@router.callback_query(F.data == "role_recruiter")
async def start_recruiter(callback: CallbackQuery, state: FSMContext):
    """Начало регистрации рекрутера"""
    await state.set_state(RecruiterRegistration.company_name)
    await callback.message.answer("🏢 Введите название компании:")
    await callback.answer()


@router.message(RecruiterRegistration.company_name, ~F.text.startswith("/"))
async def rec_company(message: Message, state: FSMContext):
    """Шаг 1: Сохраняем название компании в FSM"""
    await state.update_data(company_name=message.text.strip())
    await state.set_state(RecruiterRegistration.full_name)
    await message.answer("👤 Введите ваше ФИО:")


@router.message(RecruiterRegistration.full_name, ~F.text.startswith("/"))
async def rec_full_name(message: Message, state: FSMContext):
    """Шаг 2: Сохраняем ФИО в FSM"""
    await state.update_data(full_name=message.text.strip())
    await state.set_state(RecruiterRegistration.position)
    await message.answer("💼 Введите вашу должность:")


@router.message(RecruiterRegistration.position, ~F.text.startswith("/"))
async def rec_finish(message: Message, state: FSMContext):
    """Шаг 3: Сохраняем должность и всё записываем в БД"""
    data = await state.get_data()
    company_name = (data.get("company_name") or "").strip()
    full_name = (data.get("full_name") or "").strip()
    position = (message.text or "").strip()

    if not company_name:
        await message.answer("Не вижу компанию. Напишите /start и начните заново.")
        await state.clear()
        return

    if not full_name:
        await message.answer("Не вижу ФИО. Напишите /start и начните заново.")
        await state.clear()
        return

    tg_id = message.from_user.id

    async for session in get_session():
        res = await session.execute(select(Company).where(Company.name == company_name))
        company = res.scalar_one_or_none()
        if company is None:
            company = Company(name=company_name)
            session.add(company)
            await session.flush()

        res = await session.execute(select(User).where(User.telegram_id == tg_id))
        user = res.scalar_one_or_none()
        if user is None:
            user = User(
                telegram_id=tg_id,
                username=message.from_user.username,
                role="recruiter"
            )
            session.add(user)
            await session.flush()
        else:
            user.role = "recruiter"

        res = await session.execute(select(Recruiter).where(Recruiter.user_id == user.id))
        recruiter = res.scalar_one_or_none()
        if recruiter is None:
            recruiter = Recruiter(
                user_id=user.id,
                full_name=full_name,
                position=position,
                is_approved=False,
            )
            session.add(recruiter)
            await session.flush()
        else:
            recruiter.full_name = full_name
            recruiter.position = position
            recruiter.is_approved = False

        await session.execute(
            delete(RecruiterCompany).where(
                RecruiterCompany.recruiter_id == recruiter.id
            )
        )
        session.add(
            RecruiterCompany(recruiter_id=recruiter.id, company_id=company.id))

        existing_pending = await session.execute(
            select(RecruiterApplication).where(
                RecruiterApplication.recruiter_id == recruiter.id,
                RecruiterApplication.status == "pending",
            )
        )
        if existing_pending.scalar_one_or_none() is None:
            max_num_result = await session.execute(
                select(
                    sql_func.coalesce(sql_func.max(RecruiterApplication.application_number), 0)
                )
            )
            next_number = (max_num_result.scalar() or 0) + 1

            session.add(
                RecruiterApplication(
                    application_number=next_number,
                    recruiter_id=recruiter.id,
                    company_id=company.id,
                    status="pending",
                )
            )

        max_num_result = await session.execute(
            select(sql_func.coalesce(
                sql_func.max(RecruiterApplication.application_number), 0
            ))
        )
        next_number = max_num_result.scalar() + 1


        await session.commit()

    await state.clear()
    await message.answer(
        "⏳ Ваша заявка принята!\n\n"
        f"🏢 Компания: {company_name}\n"
        f"👤 ФИО: {full_name}\n"
        f"💼 Должность: {position}\n\n"
        "Администратор проверит ваши данные.",
        reply_markup=recruiter_pending_menu()
    )