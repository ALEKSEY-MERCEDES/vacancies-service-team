import asyncio
from db.schemas import UserCreate

async def create_user_stub(user: UserCreate):
    await asyncio.sleep(0.1)
    print(f"[STUB] User saved: {user}")
    return user

async def check_user_stub(telegram_id: int) -> UserCreate | None:
    # Пока всегда возвращает None
    return None
