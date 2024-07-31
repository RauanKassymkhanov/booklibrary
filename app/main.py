from fastapi import FastAPI
from app.config import get_settings
from alembic import command
from alembic.config import Config
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "alembic")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.sqlalchemy_database_url)

    command.upgrade(alembic_cfg, "head")

    yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    return app


app = create_app()
