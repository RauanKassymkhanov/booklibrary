from datetime import datetime

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.api.authors.schemas import Author
from app.api.books.schemas import FullBookInfo
from app.api.genres.schemas import Genre
from app.api.users.schemas import User
from app.api.utils import get_password_hash
from app.models import GenreModel, AuthorModel, BookModel, UserModel, SubscriptionModel
from app.models.base import BooksAuthors, BooksGenres
from app.tests.factory_schemas import GenreCreateFactory, AuthorCreateFactory, BookCreateFactory, UserCreateFactory


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


async def create_test_book(session: AsyncSession, title: str | None) -> FullBookInfo:
    authors = [await create_test_author(session, f"author_{i}") for i in range(2)]
    genres = [await create_test_genre(session, f"genre_{i}") for i in range(2)]
    book = BookCreateFactory.build()

    if title:
        book.title = title

    query = insert(BookModel).values(**book.model_dump(exclude={"author_ids", "genre_ids"})).returning(BookModel)
    book_db = await session.scalar(query)

    author_query = insert(BooksAuthors).values([{"book_id": book_db.id, "author_id": author.id} for author in authors])
    await session.execute(author_query)

    genre_query = insert(BooksGenres).values([{"book_id": book_db.id, "genre_id": genre.id} for genre in genres])
    await session.execute(genre_query)

    await session.commit()
    query = select(BookModel).options(selectinload(BookModel.authors)).options(selectinload(BookModel.genres))
    result = await session.execute(query)
    book = result.scalar()

    return FullBookInfo.model_validate(book)


async def create_test_user(session: AsyncSession, username: str | None) -> User:
    user = UserCreateFactory.build()
    if username:
        user.username = username
    hashed_password = get_password_hash(user.password)
    user_data = user.model_dump()
    user_data["password_hash"] = hashed_password
    del user_data["password"]

    query = insert(UserModel).values(**user_data).returning(UserModel)
    user_db = await session.scalar(query)
    return User.model_validate(user_db)


async def subscribe_user_to_author(session: AsyncSession, user_id: str, author_id: int) -> None:
    subscription_query = (
        insert(SubscriptionModel)
        .values(user_id=user_id, author_id=author_id, subscribed_date=datetime.now())
        .returning(SubscriptionModel)
    )
    await session.execute(subscription_query)
