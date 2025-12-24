import asyncio
from sqlalchemy import text

from src.infrastructure.db.session import engine


async def main():
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT 1"))
        print("DB OK:", res.scalar())


if __name__ == "__main__":
    asyncio.run(main())