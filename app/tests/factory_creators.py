from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.authors.schemas import Author
from app.api.genres.schemas import Genre
from app.models import GenreModel, AuthorModel
from app.tests.factory_schemas import GenreCreateFactory, AuthorCreateFactory


async def create_test_genre(session: AsyncSession, name: str | None) -> Genre:
    genre = GenreCreateFactory.build()
    if name:
        genre.name = name

    query = insert(GenreModel).values(**genre.model_dump()).returning(GenreModel)
    genre_db = await session.scalar(query)
    return Genre.model_validate(genre_db)


async def create_test_author(session: AsyncSession, name: str | None) -> Author:
    author = AuthorCreateFactory.build()
    if name:
        author.name = name

    query = insert(AuthorModel).values(**author.model_dump()).returning(AuthorModel)
    author_db = await session.scalar(query)
    return Author.model_validate(author_db)
