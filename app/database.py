from typing import Annotated, AsyncIterable

from pydantic import PostgresDsn
from sqlalchemy import create_engine, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column
from app.config import get_settings
from app.session_manager import session_manager


def get_engine():
    settings = get_settings()
    settings.DATABASE_URL.replace('postgresql+asyncpg', 'postgresql+psycopg')
    return create_engine(settings.DATABASE_URL)


def get_session_maker():
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    str32 = Annotated[str, mapped_column(String(32))]
    intpk = Annotated[int, mapped_column(primary_key=True)]


async def get_session() -> AsyncIterable[AsyncSession]:
    async with session_manager() as session:
        yield session


from alembic.config import Config


def get_alembic_config(database_url: PostgresDsn, script_location: str = 'migrations') -> Config:
    alembic_config = Config()
    alembic_config.set_main_option('script_location', script_location)
    alembic_config.set_main_option(
        'sqlalchemy.url',
        database_url.replace('postgresql+asyncpg', 'postgresql+psycopg'),
    )
    return alembic_config


def get_db():
    SessionLocal = get_session_maker()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
