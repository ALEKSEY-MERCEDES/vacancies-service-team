from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from bot.states.recruiter import RecruiterRegistration
from infrastructure.db.session import get_session
from infrastructure.db.models import User, Recruiter, Company, RecruiterCompany
from bot.keyboards.recruiter import recruiter_pending_menu

router = Router()


@router.callback_query(F.data == "role_recruiter")
async def start_recruiter(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RecruiterRegistration.company_name)
    await callback.message.answer("Добро пожаловать! Какую компанию вы представляете?")


@router.message(RecruiterRegistration.company_name, ~F.text.startswith("/"))
async def rec_company(message: Message, state: FSMContext):
    company_name = (message.text or "").strip()
    if not company_name:
        await message.answer("Введите название компании текстом.")
        return

    await state.update_data(company_name=message.text)

    await state.set_state(RecruiterRegistration.full_name_position)
    await message.answer("Введите ваше ФИО и должность для связи.")


@router.message(
    RecruiterRegistration.full_name_position,
    ~F.text.startswith("/")
)
async def rec_finish(message: Message, state: FSMContext):
    data = await state.get_data()
    company_name = data["company_name"]
    full_name_position = message.text.strip()

    async for session in get_session():
        user = User(
            telegram_id=message.from_user.id,
            role="recruiter",
        )
        session.add(user)
        await session.flush()

        recruiter = Recruiter(
            user_id=user.id,
            full_name_position=full_name_position,
            status="pending",  # ← ВАЖНО
        )
        session.add(recruiter)

        await session.commit()

    await state.clear()
    await message.answer(
        "⏳ Ваша заявка принята. Администратор проверит ваши данные."
    )