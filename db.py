from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.pool import NullPool

from sqlmodel import Field, Session, SQLModel, create_engine, select
from sqlmodel.ext.asyncio.session import AsyncSession

from psycopg_pool import AsyncConnectionPool

from contextlib import asynccontextmanager
from dotenv import load_dotenv, dotenv_values

config = dotenv_values()
load_dotenv(".env")  # reads variables from a .env file and sets them in os.environ
from os import getenv

print(config)

DB_NAME = getenv("DB_NAME", "postgres")
DB_HOST = getenv("DB_HOST", "localhost")
DB_PORT = getenv("DB_PORT", "5432")
DB_USER = getenv("DB_USER", "user")
DB_PASS = getenv("DB_PASSWORD", "pass")

connection_string = f"{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print("Using connection string:", connection_string)

pool = AsyncConnectionPool(
    f"postgresql://{connection_string}",
    min_size=10,
    max_size=50,
    max_idle=300,
    open=False,
)

async_engine = create_async_engine(
    f"postgresql+psycopg_async://{connection_string}",
    poolclass=NullPool,
    async_creator=pool.getconn,
)

async_session = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


@asynccontextmanager
async def get_async_session():
    async with async_session() as session:
        # @event.listens_for(session.sync_session, "after_begin")
        # def receive_after_begin(session, transaction, connection):
        #     session.info["clean"] = True

        # @event.listens_for(session.sync_session, "after_flush")
        # def receive_after_flush(session, flush_context):
        #     if session.new or session.dirty or session.deleted:
        #         session.info["clean"] = False
        #     else:
        #         print("Session is clean!")

        # @event.listens_for(session.sync_session, "after_commit")
        # def receive_after_commit(session):
        #     session.info["clean"] = True

        # @event.listens_for(session.sync_session, "after_rollback")
        # def receive_after_rollback(session):
        #     session.info["clean"] = True
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            if not session.info.get("clean", True):
                raise Exception("Session is not clean after commit/rollback!")


async def get_async_session_fastapi():
    """Dependency for FastAPI routes.

    to use with `async with`, use get_async_session() instead.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            if not session.info.get("clean", True):
                raise Exception("Session is not clean after commit/rollback!")


def create_db_and_tables(sync_engine):
    SQLModel.metadata.create_all(sync_engine)


# dispose of the pool should be handled on app shutdown
async def dispose_pool():
    await pool.close()


async def dispose_async_engine():
    await async_engine.dispose()


if __name__ == "__main__":
    import models

    sync_engine = create_engine(
        f"postgresql+psycopg://{connection_string}", echo=True, future=True
    )
    create_db_and_tables(sync_engine)
