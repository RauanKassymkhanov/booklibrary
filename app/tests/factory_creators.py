from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.genres.schemas import Genre
from app.models import GenreModel
from app.tests.factory_schemas import GenreCreateFactory


async def create_test_genre(session: AsyncSession, name: str | None) -> Genre:
    genre = GenreCreateFactory.build()
    if name:
        genre.name = name

    query = insert(GenreModel).values(**genre.model_dump()).returning(GenreModel)
    genre_db = await session.scalar(query)
    return Genre.model_validate(genre_db)
