from alembic import command
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.exceptions import register_exception_handlers
from app.api.genres import routes as genres_routes
from app.config import get_settings
from app.database import get_alembic_config
from app.api.authors import routes as authors_routes
from app.api.books import routes as books_routes
from app.api.users import routes as users_routes
from app.api.authentication import routes as login_routes
from app.api.subscriptions import routes as subscriptions_routes


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
    app.include_router(users_routes.router)
    app.include_router(login_routes.router)
    app.include_router(subscriptions_routes.router)
    register_exception_handlers(app)
    return app


app = create_app()
