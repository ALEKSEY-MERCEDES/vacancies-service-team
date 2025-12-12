import asyncio
from db.schemas import UserCreate

async def create_user_stub(user: UserCreate):
    # заглушка базы
    await asyncio.sleep(0.1)
    print(f"[STUB] User saved: {user}")
    return user
