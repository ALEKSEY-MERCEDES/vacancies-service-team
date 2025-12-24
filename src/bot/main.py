import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.core.config import settings
from src.core.logging import setup_logging

from src.bot.routers import (
    start,
    registration_candidate,
    registration_recruiter,
    registration_admin,
    admin_panel,
    recruiter_common,
    recruiter_main,
    recruiter_vacancies,
    recruiter_vacancy_create,
    recruiter_vacancy_detail,
    recruiter_candidate_detail,
    recruiter_invite,
    recruiter_reject,
    recruiter_stats,
    recruiter_archive,
    candidate_vacancies,
    candidate_my_apps,
    candidate_apply,
    candidate_saved,
    candidate_block_company,
    candidate_cancel_app,
    reset,
)


async def main():
    setup_logging()

    bot = Bot(token=settings.tg_bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(registration_candidate.router)
    dp.include_router(registration_recruiter.router)
    dp.include_router(registration_admin.router)
    dp.include_router(admin_panel.router)

    dp.include_router(candidate_apply.router)
    dp.include_router(candidate_saved.router)
    dp.include_router(candidate_block_company.router)
    dp.include_router(candidate_cancel_app.router)
    dp.include_router(candidate_vacancies.router)
    dp.include_router(candidate_my_apps.router)

    dp.include_router(recruiter_common.router)
    dp.include_router(recruiter_main.router)
    dp.include_router(recruiter_vacancies.router)
    dp.include_router(recruiter_vacancy_create.router)
    dp.include_router(recruiter_vacancy_detail.router)
    dp.include_router(recruiter_candidate_detail.router)
    dp.include_router(recruiter_invite.router)
    dp.include_router(recruiter_reject.router)
    dp.include_router(recruiter_stats.router)
    dp.include_router(recruiter_archive.router)

    dp.include_router(reset.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
