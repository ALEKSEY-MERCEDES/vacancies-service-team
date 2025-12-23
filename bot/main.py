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
    admin_panel,
    recruiter_common,
    recruiter_main,
    recruiter_vacancies,
    recruiter_vacancy_create,
    recruiter_vacancy_detail,
    recruiter_responses,
    recruiter_candidate_detail,
    recruiter_invite,
    recruiter_reject,
    recruiter_stats,
    recruiter_archive,
    candidate_vacancies,
    candidate_my_apps,
    candidate_apply,  # 👈 ДОБАВИТЬ
    candidate_saved,  # 👈 ДОБАВИТЬ
    candidate_block_company,  # 👈 ДОБАВИТЬ
    candidate_cancel_app,  # 👈 ДОБАВИТЬ
    reset,
)


async def main():
    bot = Bot(token=settings.tg_bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    # Порядок важен! FSM роутеры первыми
    dp.include_router(start.router)
    dp.include_router(registration_candidate.router)
    dp.include_router(registration_recruiter.router)
    dp.include_router(registration_admin.router)
    dp.include_router(admin_panel.router)

    # Candidate FSM первым (перехватывает c:apply:)
    dp.include_router(candidate_apply.router)  # 👈 ДОБАВИТЬ (до candidate_vacancies!)
    dp.include_router(candidate_saved.router)  # 👈 ДОБАВИТЬ
    dp.include_router(candidate_block_company.router)  # 👈 ДОБАВИТЬ
    dp.include_router(candidate_cancel_app.router)  # 👈 ДОБАВИТЬ
    dp.include_router(candidate_vacancies.router)
    dp.include_router(candidate_my_apps.router)

    dp.include_router(recruiter_common.router)
    dp.include_router(recruiter_main.router)
    dp.include_router(recruiter_vacancies.router)
    dp.include_router(recruiter_vacancy_create.router)
    dp.include_router(recruiter_vacancy_detail.router)
    dp.include_router(recruiter_responses.router)
    dp.include_router(recruiter_candidate_detail.router)
    dp.include_router(recruiter_invite.router)
    dp.include_router(recruiter_reject.router)
    dp.include_router(recruiter_stats.router)
    dp.include_router(recruiter_archive.router)
    dp.include_router(reset.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())