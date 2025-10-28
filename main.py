from fastapi import FastAPI, Depends
from fastapi.responses import ORJSONResponse
from contextlib import asynccontextmanager

from sqlmodel import select
from models import User, Hero
from db import (
    dispose_pool,
    dispose_async_engine,
    pool,
    AsyncSession,
    get_async_session_fastapi,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await pool.open()
    await pool.wait()
    yield
    await dispose_pool()
    await dispose_async_engine()


app = FastAPI(default_response_class=ORJSONResponse, lifespan=lifespan)


def read_root():
    return {"Hello": "World"}


@app.get("/ping")
def read_ping():
    return "pong"


@app.post("/user")
async def create_user(
    user: User, db: AsyncSession = Depends(get_async_session_fastapi)
):
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@app.get("/user")
async def read_user(db: AsyncSession = Depends(get_async_session_fastapi)):
    user = await db.exec(select(User))
    user = user.all()
    return user


@app.get("/user/{id}")
async def read_user(id: int, db: AsyncSession = Depends(get_async_session_fastapi)):
    user = await db.exec(select(User).where(User.id == id))
    user = user.first()
    if not user:
        raise ValueError(f"User with id {id} not found")
    return user


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, env_file=".env")
