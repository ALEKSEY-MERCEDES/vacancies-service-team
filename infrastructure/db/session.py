import os
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("ASYNC_DATABASE_URL is not set")

engine = create_async_engine(DATABASE_URL, echo=False)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
