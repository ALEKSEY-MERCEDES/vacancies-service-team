from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Бот/приложение (async)
    async_database_url: str = Field(alias="ASYNC_DATABASE_URL")

    # Alembic (sync)
    database_url: str = Field(alias="DATABASE_URL")

    tg_bot_token: str = Field(alias="TG_BOT_TOKEN")


settings = Settings()
