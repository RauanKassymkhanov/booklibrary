from alembic import command
from fastapi import FastAPI
from contextlib import asynccontextmanager
from alembic.config import Config
from app.api.genres import routes
from app.config import get_settings
from app.database import get_alembic_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    alembic_cfg = get_alembic_config(settings.DATABASE_URL, "app/migrations")
    # alembic_cfg.set_main_option("script_location", "app/migrations")
    # alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    
    command.upgrade(alembic_cfg, "head")

    yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(routes.router)
    return app


app = create_app()


