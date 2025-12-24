from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from bot.states.vacancy_create import VacancyCreate
from infrastructure.db.session import get_session
from infrastructure.db.models import User, Recruiter, Vacancy, RecruiterCompany
from bot.keyboards.recruiter import vacancy_preview_menu, recruiter_main_menu

router = Router()


async def _get_recruiter_id_by_tg(session, telegram_id: int):
    res = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = res.scalar_one_or_none()
    if not user or user.role != "recruiter":
        return None, None

    res = await session.execute(select(Recruiter).where(Recruiter.user_id == user.id))
    recruiter = res.scalar_one_or_none()
    if not recruiter:
        return user, None

    return user, recruiter


async def _get_company_id_for_recruiter(session, recruiter_id):
    # Берём первую компанию рекрутера (у тебя связь многие-ко-многим)
    res = await session.execute(
        select(RecruiterCompany.company_id).where(RecruiterCompany.recruiter_id == recruiter_id)
    )
    company_id = res.scalar_one_or_none()
    return company_id


@router.callback_query(F.data == "r:create_vacancy")
async def start_create_vacancy(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(VacancyCreate.title)
    await callback.message.answer("Введите название должности (например, Python Junior)")


@router.message(VacancyCreate.title, ~F.text.startswith("/"))
async def step_title(message: Message, state: FSMContext):
    title = (message.text or "").strip()
    if not title:
        await message.answer("Введите название текстом.")
        return

    await state.update_data(title=title)
    await state.set_state(VacancyCreate.description)
    await message.answer("Опишите требования и обязанности (текстом).")


@router.message(VacancyCreate.description, ~F.text.startswith("/"))
async def step_description(message: Message, state: FSMContext):
    desc = (message.text or "").strip()
    if not desc:
        await message.answer("Введите описание текстом.")
        return

    await state.update_data(description=desc)
    await state.set_state(VacancyCreate.salary)
    await message.answer("Укажите диапазон зарплаты (например: 50000-80000).")


@router.message(VacancyCreate.salary, ~F.text.startswith("/"))
async def step_salary(message: Message, state: FSMContext):
    salary = (message.text or "").strip()
    if not salary:
        await message.answer("Введите диапазон зарплаты текстом.")
        return

    await state.update_data(salary=salary)
    await state.set_state(VacancyCreate.city)
    await message.answer("Какой город? (или 'Удаленно')")


@router.message(VacancyCreate.city, ~F.text.startswith("/"))
async def step_city_and_preview(message: Message, state: FSMContext):
    city = (message.text or "").strip()
    if not city:
        await message.answer("Введите город текстом.")
        return

    data = await state.get_data()
    title = data["title"]
    description = data["description"]
    salary = data["salary"]

    # Собираем единый description, чтобы не менять БД
    full_description = (
        f"📍 Город: {city}\n"
        f"💰 Зарплата: {salary}\n\n"
        f"{description}"
    )

    async for session in get_session():
        user, recruiter = await _get_recruiter_id_by_tg(session, message.from_user.id)
        if not user or not recruiter:
            await message.answer("Сначала зарегистрируйтесь как рекрутер.")
            return

        # Берём company_id из связки recruiter_companies
        company_id = await _get_company_id_for_recruiter(session, recruiter.id)
        if not company_id:
            await message.answer("Не нашёл компанию рекрутера в базе. Перерегистрируйся (или проверь recruiter_companies).")
            return

        vacancy = Vacancy(
            title=title,
            description=full_description,
            status="open",  # сразу open; можно сделать draft, если добавишь статус
            company_id=company_id,
            recruiter_id=recruiter.id,
        )
        session.add(vacancy)
        await session.flush()
        vacancy_id = str(vacancy.id)
        await session.commit()

    await state.clear()

    # Preview как в макете
    await message.answer(
        "Проверьте вакансию перед публикацией:\n\n"
        f"💼 {title}\n"
        f"{full_description}",
        reply_markup=vacancy_preview_menu(vacancy_id),
    )


@router.callback_query(F.data.startswith("recruiter_vacancy_publish:"))
async def publish_vacancy(callback: CallbackQuery):
    vacancy_id = callback.data.split(":", 1)[1]

    # сейчас вакансия и так open, поэтому просто подтверждаем
    await callback.message.answer(
        "✅ Вакансия опубликована!",
        reply_markup=recruiter_main_menu(),
    )


@router.callback_query(F.data == "recruiter_vacancy_cancel")
async def cancel_create(callback: CallbackQuery):
    await callback.message.answer(
        "❌ Создание вакансии отменено.",
        reply_markup=recruiter_main_menu(),
    )
