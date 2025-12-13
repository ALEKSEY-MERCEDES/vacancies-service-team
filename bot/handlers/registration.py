from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from db.schemas import UserCreate
from db.repo import create_user_stub

class RegStates(StatesGroup):
    waiting_for_role = State()
    waiting_for_name = State()
    waiting_for_resume = State()

def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(role_chosen, RegStates.waiting_for_role)
    dp.message.register(name_received, RegStates.waiting_for_name)
    dp.message.register(resume_received, RegStates.waiting_for_resume)

async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    # Кнопки только для Соискателя и Рекрутера
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton("Соискатель")],
            [types.KeyboardButton("Рекрутер")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите роль (или введите 'Админ' вручную):", reply_markup=keyboard)
    await state.set_state(RegStates.waiting_for_role)

async def role_chosen(message: Message, state: FSMContext):
    role = message.text.strip().lower()
    if role not in {"соискатель", "рекрутер", "админ"}:
        await message.answer("Пожалуйста, выберите роль из кнопок или введите 'Админ' вручную")
        return
    await state.update_data(role=role)
    await message.answer("Введите ваше имя:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(RegStates.waiting_for_name)

async def name_received(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())

    # Шаг 3: выбор типа резюме через кнопки
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton("Прислать текст резюме")],
            [types.KeyboardButton("Отправить файл резюме")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "Пришлите текстовое резюме или выберите вариант 'Отправить файл':",
        reply_markup=keyboard
    )
    await state.set_state(RegStates.waiting_for_resume)

async def resume_received(message: Message, state: FSMContext):
    data = await state.get_data()

    if message.text and message.text not in {"Прислать текст резюме", "Отправить файл резюме"}:
        resume_text = message.text
    else:
        resume_text = "[файл прикреплен]"

    user = UserCreate(
        telegram_id=message.from_user.id,
        role=data["role"],
        name=data["name"],
        resume=resume_text
    )

    # заглушка
    await create_user_stub(user)

    await message.answer("Регистрация завершена!", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()
