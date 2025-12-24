from aiogram.fsm.state import StatesGroup, State


class VacancyCreate(StatesGroup):
    title = State()
    description = State()
    salary = State()
    city = State()
    preview = State()