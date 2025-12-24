from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from src.bot.states.candidate import CandidateRegistration
from src.bot.keyboards.common import candidate_menu
from src.bot.utils.files import is_valid_resume
from src.infrastructure.db.session import get_session
from src.infrastructure.db.models import User, Candidate
import logging
logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == "role_candidate")
async def start_candidate(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CandidateRegistration.full_name)
    await callback.message.answer("Введите ФИО:")


@router.message(CandidateRegistration.full_name, ~F.text.startswith("/"))
async def cand_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(CandidateRegistration.age)
    await message.answer("Введите возраст:")


@router.message(CandidateRegistration.age, ~F.text.startswith("/"))
async def cand_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(CandidateRegistration.skills)
    await message.answer("Введите навыки:")


@router.message(CandidateRegistration.skills, ~F.text.startswith("/"))
async def cand_skills(message: Message, state: FSMContext):
    await state.update_data(skills=message.text)
    await state.set_state(CandidateRegistration.current_company)
    await message.answer("Введите текущую компанию (или '-'):")


@router.message(CandidateRegistration.current_company, ~F.text.startswith("/"))
async def cand_company(message: Message, state: FSMContext):
    await state.update_data(current_company=message.text)
    await state.set_state(CandidateRegistration.resume)
    await message.answer("Загрузите резюме (PDF / DOCX, до 20 МБ):")


@router.message(CandidateRegistration.resume, F.text, ~F.text.startswith("/"))
async def cand_resume_wrong(message: Message, state: FSMContext):
    await message.answer("Пришлите файл резюме (PDF/DOCX), пожалуйста 🙂")



@router.message(CandidateRegistration.resume, F.document)
async def cand_resume(message: Message, state: FSMContext):
    if not is_valid_resume(message.document):
        await message.answer("Неверный формат или файл слишком большой")
        return


    data = await state.get_data()
    full_name = data.get("full_name")
    age_raw = data.get("age")
    skills = data.get("skills")
    current_company = data.get("current_company")

    try:
        age = int(age_raw) if age_raw is not None else None
    except ValueError:
        await message.answer("Возраст должен быть числом. Введите возраст ещё раз:")
        await state.set_state(CandidateRegistration.age)
        return

    resume_file_id = message.document.file_id

    async for session in get_session():
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                role="candidate",
            )
            session.add(user)
            await session.flush()
        else:
            user.role = "candidate"

        result = await session.execute(
            select(Candidate).where(Candidate.user_id == user.id)
        )
        candidate = result.scalar_one_or_none()

        if candidate is None:
            candidate = Candidate(user_id=user.id)
            session.add(candidate)

        candidate.full_name = full_name
        candidate.age = age
        candidate.skills = skills
        candidate.current_company = current_company
        candidate.resume_file_id = resume_file_id

        await session.commit()

    await state.clear()
    await message.answer("Профиль создан ✅", reply_markup=candidate_menu())


