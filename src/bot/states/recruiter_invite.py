from aiogram.fsm.state import StatesGroup, State


class RecruiterInvite(StatesGroup):
    message = State()