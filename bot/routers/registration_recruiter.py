from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.states.recruiter import RecruiterRegistration
from infrastructure.db.session import get_session
from infrastructure.db.models import User, Recruiter

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


@router.message(RecruiterRegistration.full_name_position)
async def rec_finish(message: Message, state: FSMContext):
    async for session in get_session():
        user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            role="recruiter",
        )
        session.add(user)
        await session.flush()

        session.add(Recruiter(user_id=user.id))
        await session.commit()

    await state.clear()
    await message.answer("Заявка отправлена на модерацию ⏳")
