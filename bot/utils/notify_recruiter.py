from aiogram import Bot
from sqlalchemy import select

from infrastructure.db.models import Recruiter, User, Vacancy, Company
from infrastructure.db.session import get_session


async def notify_recruiter_new_application(
    bot: Bot,
    recruiter_id,
    vacancy_id,
    candidate_name: str,
):
    async for session in get_session():
        res = await session.execute(
            select(
                User.telegram_id,
                Vacancy.title,
                Company.name,
            )
            .join(Recruiter, Recruiter.user_id == User.id)
            .join(Vacancy, Vacancy.company_id == Company.id)
            .where(Recruiter.id == recruiter_id, Vacancy.id == vacancy_id)
        )
        row = res.first()

        if not row:
            return

        tg_id, vacancy_title, company_name = row

    text = (
        f"📩 <b>Новый отклик</b>\n\n"
        f"👤 Кандидат: <b>{candidate_name}</b>\n"
        f"💼 Вакансия: <b>{vacancy_title}</b>\n"
        f"🏢 Компания: <b>{company_name}</b>"
    )

    await bot.send_message(
        chat_id=tg_id,
        text=text,
        parse_mode="HTML",
    )
