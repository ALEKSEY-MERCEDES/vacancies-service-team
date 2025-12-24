from aiogram.fsm.state import StatesGroup, State


class CandidateApply(StatesGroup):
    """FSM для отклика с сообщением"""
    message = State()