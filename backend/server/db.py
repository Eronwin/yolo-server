import re
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import event

from backend.config.envs import DB_ECHO, DB_MAX_OVERFLOW, DB_POOL_SIZE, DB_POOL_TIMEOUT
from backend.schemas.users import User

_engine = None


def get_engine():
    return _engine


async def get_session():
    async with AsyncSession(_engine) as session:
        yield session


@asynccontextmanager
async def get_session_context():
    async with AsyncSession(_engine) as session:
        yield session


async def init_db(db_url: str):
    global _engine, _session_maker
    if _engine is None:
        connect_args = {}
        if db_url.startswith("sqlite://"):
            connect_args = {"check_same_thread": False}
            # use async driver
            db_url = re.sub(r"^sqlite://", "sqlite+aiosqlite://", db_url)
        elif db_url.startswith("postgresql://"):
            db_url = re.sub(r"^postgresql://", "postgresql+asyncpg://", db_url)
        elif db_url.startswith("mysql://"):
            db_url = re.sub(r"^mysql://", "mysql+asyncmy://", db_url)
        else:
            raise Exception(f"Unsupported database URL: {db_url}")

        _engine = create_async_engine(
            db_url,
            echo=DB_ECHO,
            pool_size=DB_POOL_SIZE,
            max_overflow=DB_MAX_OVERFLOW,
            pool_timeout=DB_POOL_TIMEOUT,
            connect_args=connect_args,
        )
        listen_events(_engine)
    await create_db_and_tables(_engine)


async def create_db_and_tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(
            SQLModel.metadata.create_all,
            tables=[
                User.__table__,
            ],
        )


def listen_events(engine: AsyncEngine):
    if engine.dialect.name == "postgresql":
        pass
    elif engine.dialect.name == "mysql":
        pass
    else:
        pass

    if engine.dialect.name == "sqlite":
        event.listen(engine.sync_engine, "connect", enable_sqlite_foreign_keys)


def enable_sqlite_foreign_keys(conn, record):
    # Enable foreign keys for SQLite, since it's disabled by default
    conn.execute("PRAGMA foreign_keys=ON")
