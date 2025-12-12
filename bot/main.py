import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot.handlers.registration import register_handlers
from dotenv import load_dotenv

load_dotenv()  # загружаем токены из .env

TOKEN = os.getenv("TG_BOT_TOKEN")

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    register_handlers(dp)
    print("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
