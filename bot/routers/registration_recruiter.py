from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.states.recruiter import RecruiterRegistration
from infrastructure.db.session import get_session
from infrastructure.db.models import User, Recruiter
from sqlalchemy import select
router = Router()


@router.callback_query(F.data == "role_recruiter")
async def start_recruiter(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RecruiterRegistration.company_name)
    await callback.message.answer("Введите название компании:")


@router.message(RecruiterRegistration.company_name)
async def rec_company(message: Message, state: FSMContext):
    await state.update_data(company=message.text)
    await state.set_state(RecruiterRegistration.full_name_position)
    await message.answer("Введите ФИО и должность:")


from sqlalchemy import select

@router.message(RecruiterRegistration.full_name_position, ~F.text.startswith("/"))
async def rec_finish(message: Message, state: FSMContext):
    data = await state.get_data()
    company_name = data.get("company")
    full_name_position = message.text

    async for session in get_session():
        res = await session.execute(select(User).where(User.telegram_id == message.from_user.id))
        user = res.scalar_one_or_none()

        if user is None:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                role="recruiter",
            )
            session.add(user)
            await session.flush()
        else:
            user.role = "recruiter"

        res = await session.execute(select(Recruiter).where(Recruiter.user_id == user.id))
        recruiter = res.scalar_one_or_none()

        if recruiter is None:
            recruiter = Recruiter(user_id=user.id)
            session.add(recruiter)

        # если у Recruiter есть поля:
        # recruiter.company_name = company_name
        # recruiter.full_name_position = full_name_position

        await session.commit()

    await state.clear()
    await message.answer("Заявка отправлена на модерацию ⏳")
