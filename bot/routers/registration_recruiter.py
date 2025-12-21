from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func as sql_func

from bot.states.recruiter import RecruiterRegistration

from infrastructure.db.session import get_session
from infrastructure.db.models import User, Recruiter, RecruiterApplication, \
    Company, RecruiterCompany

router = Router()


@router.callback_query(F.data == "role_recruiter")
async def start_recruiter(callback: CallbackQuery, state: FSMContext):
    """Начало регистрации рекрутера"""
    await state.set_state(RecruiterRegistration.company_name)
    await callback.message.answer("🏢 Введите название компании:")
    await callback.answer()


@router.message(RecruiterRegistration.company_name, ~F.text.startswith("/"))
async def rec_company(message: Message, state: FSMContext):
    """Шаг 1: Сохраняем название компании в FSM и переходим к следующему шагу"""
    await state.update_data(company_name=message.text.strip())
    await state.set_state(RecruiterRegistration.full_name)
    await message.answer("👤 Введите ваше ФИО:")


@router.message(RecruiterRegistration.full_name, ~F.text.startswith("/"))
async def rec_full_name(message: Message, state: FSMContext):
    """Шаг 2: Сохраняем ФИО в FSM и переходим к следующему шагу"""
    await state.update_data(full_name=message.text.strip())
    await state.set_state(RecruiterRegistration.position)
    await message.answer("💼 Введите вашу должность:")


from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

@router.message(RecruiterRegistration.full_name_position, ~F.text.startswith("/"))
async def rec_finish(message: Message, state: FSMContext):
    data = await state.get_data()
    company_name = (data.get("company_name") or "").strip()
    full_name_position = (message.text or "").strip()

    if not company_name:
        await message.answer("Не вижу компанию. Напишите /start и начните заново.")
        return

    tg_id = message.from_user.id

    # парсинг "ФИО и должность"
    # (пока простая версия: всё в одну строку, потом улучшим)
    full_name = full_name_position
    position = None

    async for session in get_session():
        # 1) Company: найти или создать
        res = await session.execute(select(Company).where(Company.name == company_name))
        company = res.scalar_one_or_none()
        if company is None:
            company = Company(name=company_name)
            session.add(company)
            await session.flush()  # <-- ВАЖНО: получаем company.id

        # 2) User: найти или создать (и НИГДЕ не передавать username, если колонки нет)
        res = await session.execute(select(User).where(User.telegram_id == tg_id))
        user = res.scalar_one_or_none()
        if user is None:
            user = User(telegram_id=tg_id, role="recruiter")
            session.add(user)
            await session.flush()
        else:
            user.role = "recruiter"
            await session.flush()

        # 3) Recruiter: найти или создать
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
            await session.flush()

        # 4) Связка recruiter_companies: убедиться что её нет, и добавить
        # (без этого может быть дубль)
        await session.execute(
            delete(RecruiterCompany).where(
                RecruiterCompany.recruiter_id == recruiter.id,
                RecruiterCompany.company_id == company.id,
            )
        )
        session.add(RecruiterCompany(recruiter_id=recruiter.id, company_id=company.id))

        await session.commit()

    await state.clear()
    await message.answer("⏳ Ваша заявка принята. Администратор проверит ваши данные.")
