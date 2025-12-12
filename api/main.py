from fastapi import FastAPI
from db.schemas import UserCreate
from db.repo import create_user_stub

app = FastAPI(title="Vacancies Bot API")

@app.post("/users/")
async def create_user(user: UserCreate):
    created = await create_user_stub(user)
    return {"status": "ok", "user": created}
