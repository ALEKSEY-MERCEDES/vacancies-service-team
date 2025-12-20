import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from infrastructure.config import settings
from bot.routers import start, registration_candidate, registration_recruiter


async def main():
    bot = Bot(token=settings.tg_bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(registration_candidate.router)
    dp.include_router(registration_recruiter.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
