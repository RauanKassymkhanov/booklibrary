from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Annotated, AsyncIterable
from pydantic import PostgresDsn
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, mapped_column
from app.config import get_settings
from alembic.config import Config


class Base(DeclarativeBase):
    str32 = Annotated[str, mapped_column(String(32))]
    intpk = Annotated[int, mapped_column(primary_key=True)]


def get_alembic_config(database_url: PostgresDsn, script_location: str = "migrations") -> Config:
    alembic_config = Config()
    alembic_config.set_main_option("script_location", script_location)
    alembic_config.set_main_option(
        "sqlalchemy.url",
        database_url.replace("postgresql+asyncpg", "postgresql+psycopg"),
    )
    return alembic_config


@lru_cache
def async_engine() -> AsyncEngine:
    settings = get_settings()
    return create_async_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        echo=True,
    )


@lru_cache
def async_session_factory() -> async_sessionmaker:
    return async_sessionmaker(
        bind=async_engine(),
        autoflush=False,
        expire_on_commit=False,
    )


async def get_session() -> AsyncIterable[AsyncSession]:
    async with get_managed_session() as session:
        yield session


@asynccontextmanager
async def get_managed_session() -> AsyncSession:
    factory: async_sessionmaker = async_session_factory()
    session: AsyncSession = factory()
    try:
        yield session
    except Exception as e:
        await session.rollback()
        raise e
    else:
        await session.commit()
    finally:
        await session.close()
