from aiogram.fsm.state import StatesGroup, State


class RecruiterRegistration(StatesGroup):
    company_name = State()
    full_name_position = State()
