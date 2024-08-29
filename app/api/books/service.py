from fastapi import BackgroundTasks, Depends
from sqlalchemy import select, insert, update, delete
from pydantic import TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.api.subscriptions.email_service import EmailService
from app.database import get_session, Base
from app.models import AuthorModel, GenreModel, SubscriptionModel
from app.models.base import BooksAuthors, BooksGenres
from app.models.books import BookModel
from app.api.books.schemas import BookCreate, FullBookInfo
from app.api.base_service import BaseService
from app.api.exceptions import NotFoundError


class BookService(BaseService):
    def __init__(self, email_service: EmailService = Depends(), session: AsyncSession = Depends(get_session)):
        super().__init__(session)
        self.email_service = email_service

    async def get_books(self) -> list[FullBookInfo]:
        query = select(BookModel).options(selectinload(BookModel.authors)).options(selectinload(BookModel.genres))
        result = await self._session.execute(query)
        books = result.scalars().all()
        return TypeAdapter(list[FullBookInfo]).validate_python(books)

    async def create_book(self, new_book: BookCreate, background_tasks: BackgroundTasks) -> FullBookInfo:
        await self._validate_ids_or_raise(AuthorModel, new_book.author_ids, "Author")
        await self._validate_ids_or_raise(GenreModel, new_book.genre_ids, "Genre")

        book_query = (
            insert(BookModel).values(**new_book.model_dump(exclude={"author_ids", "genre_ids"})).returning(BookModel)
        )
        book_result = await self._session.scalar(book_query)
        book_id = book_result.id

        authors_query = insert(BooksAuthors).values(
            [{"book_id": book_id, "author_id": author_id} for author_id in new_book.author_ids]
        )
        await self._session.execute(authors_query)

        genres_query = insert(BooksGenres).values(
            [{"book_id": book_id, "genre_id": genre_id} for genre_id in new_book.genre_ids]
        )
        await self._session.execute(genres_query)

        await self._notify_subscribers(new_book.author_ids, book_result, background_tasks)

        return await self._get_book_or_raise(book_id)

    async def get_book(self, book_id: int) -> FullBookInfo:
        return await self._get_book_or_raise(book_id)

    async def delete_book(self, book_id: int) -> None:
        await self._get_book_or_raise(book_id)
        delete_query = delete(BookModel).where(BookModel.id == book_id)
        await self._session.execute(delete_query)

    async def update_book(self, book_id: int, updated_book: BookCreate) -> FullBookInfo:
        await self._validate_ids_or_raise(AuthorModel, updated_book.author_ids, "Author")
        await self._validate_ids_or_raise(GenreModel, updated_book.genre_ids, "Genre")
        await self._get_book_or_raise(book_id)
        update_query = (
            update(BookModel)
            .values(**updated_book.model_dump(exclude={"author_ids", "genre_ids"}))
            .where(BookModel.id == book_id)
            .returning(BookModel)
        )
        book_update = await self._session.scalar(update_query)
        book_id = book_update.id

        delete_authors_query = delete(BooksAuthors).where(BooksAuthors.book_id == book_id)
        await self._session.execute(delete_authors_query)

        authors_query = insert(BooksAuthors).values(
            [{"book_id": book_id, "author_id": author_id} for author_id in updated_book.author_ids]
        )
        await self._session.execute(authors_query)

        delete_genres_query = delete(BooksGenres).where(BooksGenres.book_id == book_id)
        await self._session.execute(delete_genres_query)

        genres_query = insert(BooksGenres).values(
            [{"book_id": book_id, "genre_id": genre_id} for genre_id in updated_book.genre_ids]
        )
        await self._session.execute(genres_query)

        return await self._get_book_or_raise(book_id)

    async def _get_book_or_raise(self, book_id: int) -> FullBookInfo:
        query = (
            select(BookModel)
            .options(selectinload(BookModel.authors))
            .options(selectinload(BookModel.genres))
            .where(BookModel.id == book_id)
        )
        result = await self._session.execute(query)
        book = result.scalar_one_or_none()

        if book is None:
            raise NotFoundError("Book", book_id)
        return FullBookInfo.model_validate(book)

    async def _notify_subscribers(
        self, author_ids: list[int], book: BookModel, background_tasks: BackgroundTasks
    ) -> None:
        subscribers_query = (
            select(SubscriptionModel)
            .options(selectinload(SubscriptionModel.users), selectinload(SubscriptionModel.authors))
            .where(SubscriptionModel.author_id.in_(author_ids))
        )
        result = await self._session.execute(subscribers_query)
        subscribers = result.scalars().all()

        for subscription in subscribers:
            user_email = subscription.users.email
            author_name = subscription.authors.name
            subject = f"New Book by {author_name}"
            message = (
                f"A new book titled '{book.title}' by {author_name} has been added to our library.\n\nCheck it out!"
            )

            background_tasks.add_task(self.email_service.send_email, user_email, subject, message)

    async def _validate_ids_or_raise(self, model: type[Base], ids: list[int], entity_name: str) -> None:
        query = select(model).where(model.id.in_(ids))
        result = await self._session.scalars(query)

        existing_ids = {item.id for item in result}
        missing_ids = set(ids) - existing_ids

        if missing_ids:
            raise NotFoundError(entity_name, missing_ids)
