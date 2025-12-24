from aiogram.fsm.state import StatesGroup, State


class RecruiterRegistration(StatesGroup):
    company_name = State()      # Шаг 1: название компании
    full_name = State()         # Шаг 2: ФИО
    position = State()          # Шаг 3: должность