import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()

from infrastructure.config import settings
from bot.routers import (
    start,
    registration_candidate,
    registration_recruiter,
    registration_admin,
    admin_panel,  # ← ДОБАВИТЬ
    recruiter_common,
    recruiter_main,
    reset,
)


async def main():
    bot = Bot(token=settings.tg_bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(registration_candidate.router)
    dp.include_router(registration_recruiter.router)
    dp.include_router(registration_admin.router)
    dp.include_router(admin_panel.router)  # ← ДОБАВИТЬ
    dp.include_router(recruiter_common.router)
    dp.include_router(recruiter_main.router)
    dp.include_router(reset.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())