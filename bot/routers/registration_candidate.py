from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.states.candidate import CandidateRegistration
from bot.keyboards.common import candidate_menu
from bot.utils.files import is_valid_resume
from infrastructure.db.session import get_session
from infrastructure.db.models import User, Candidate

router = Router()


@router.callback_query(F.data == "role_candidate")
async def start_candidate(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CandidateRegistration.full_name)
    await callback.message.answer("Введите ФИО:")


@router.message(CandidateRegistration.full_name)
async def cand_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(CandidateRegistration.age)
    await message.answer("Введите возраст:")


@router.message(CandidateRegistration.age)
async def cand_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(CandidateRegistration.skills)
    await message.answer("Введите навыки:")


@router.message(CandidateRegistration.skills)
async def cand_skills(message: Message, state: FSMContext):
    await state.update_data(skills=message.text)
    await state.set_state(CandidateRegistration.current_company)
    await message.answer("Введите текущую компанию (или '-'):")


@router.message(CandidateRegistration.current_company)
async def cand_company(message: Message, state: FSMContext):
    await state.set_state(CandidateRegistration.resume)
    await message.answer("Загрузите резюме (PDF / DOCX, до 20 МБ):")


@router.message(CandidateRegistration.resume, F.document)
async def cand_resume(message: Message, state: FSMContext):
    if not is_valid_resume(message.document):
        await message.answer("Неверный формат или файл слишком большой")
        return

    async for session in get_session():
        user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            role="candidate",
        )
        session.add(user)
        await session.flush()

        session.add(Candidate(user_id=user.id))
        await session.commit()

    await state.clear()
    await message.answer("Профиль создан ✅", reply_markup=candidate_menu())
