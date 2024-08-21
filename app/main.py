from alembic import command
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.genres import routes as genres_routes
from app.config import get_settings
from app.database import get_alembic_config
from app.api.authors import routes as authors_routes
from app.api.books import routes as books_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    alembic_cfg = get_alembic_config(settings.DATABASE_URL, "app/migrations")
    command.upgrade(alembic_cfg, "head")

    yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(genres_routes.router)
    app.include_router(authors_routes.router)
    app.include_router(books_routes.router)
    return app


app = create_app()
