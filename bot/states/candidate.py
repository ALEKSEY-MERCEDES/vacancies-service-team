from aiogram.fsm.state import StatesGroup, State


class CandidateRegistration(StatesGroup):
    full_name = State()
    age = State()
    skills = State()
    current_company = State()
    resume = State()
