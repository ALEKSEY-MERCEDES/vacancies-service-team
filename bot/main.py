import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from bot.routers import admin_panel
load_dotenv()
from bot.routers import registration_admin
from bot.routers import recruiter_common
from infrastructure.config import settings
from bot.routers import candidate_vacancies
from bot.routers import start, registration_candidate, registration_recruiter, registration_admin, reset
from bot.routers import candidate_my_apps
from bot.routers import recruiter_vacancy_detail
from bot.routers import recruiter_stats
from bot.routers import recruiter_archive


from bot.routers import (
    start, registration_candidate, registration_recruiter, registration_admin, reset,
    recruiter_common, recruiter_main,
    recruiter_vacancy_create, recruiter_vacancies, recruiter_vacancy_detail,
    recruiter_responses, recruiter_candidate_detail, recruiter_invite, recruiter_reject,
    admin_panel,
)


async def main():
    bot = Bot(token=settings.tg_bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(registration_candidate.router)
    dp.include_router(registration_recruiter.router)
    dp.include_router(reset.router)
    dp.include_router(recruiter_common.router)
    dp.include_router(recruiter_stats.router)
    dp.include_router(candidate_vacancies.router)
    dp.include_router(candidate_my_apps.router)
    dp.include_router(admin_panel.router)
    dp.include_router(registration_admin.router)
    dp.include_router(recruiter_main.router)
    dp.include_router(recruiter_archive.router)
    dp.include_router(recruiter_vacancy_create.router)
    dp.include_router(recruiter_vacancies.router)
    dp.include_router(recruiter_vacancy_detail.router)
    dp.include_router(recruiter_responses.router)
    dp.include_router(recruiter_candidate_detail.router)
    dp.include_router(recruiter_invite.router)
    dp.include_router(recruiter_reject.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
