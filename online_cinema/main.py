from fastapi import FastAPI

from database import engine
from models import Base
from routers import users, movies

app = FastAPI()

app.include_router(users.router)
app.include_router(movies.router)


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
