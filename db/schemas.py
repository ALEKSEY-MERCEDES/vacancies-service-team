from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    telegram_id: int = Field(..., example=123456)
    role: str = Field(..., example="соискатель")
    name: str = Field(..., example="Иван")
    resume: str | None = Field(None, example="Резюме текстом")
