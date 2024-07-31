from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import get_settings


def get_engine():
    settings = get_settings()
    return create_engine(settings.sqlalchemy_database_url)


def get_session_maker():
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    abstract = True


def get_db():
    SessionLocal = get_session_maker()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
