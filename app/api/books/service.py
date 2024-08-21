from sqlalchemy import select, insert, update, delete
from pydantic import TypeAdapter
from sqlalchemy.orm import selectinload
from app.models import AuthorModel, GenreModel
from app.models.base import BooksAuthors, BooksGenres
from app.models.books import BookModel
from app.api.books.schemas import BookCreate, FullBookInfo
from app.api.base_service import BaseService
from app.api.exceptions import NotFoundError


class BookService(BaseService):
    async def get_books(self) -> list[FullBookInfo]:
        query = select(BookModel).options(selectinload(BookModel.authors)).options(selectinload(BookModel.genres))
        result = await self._session.execute(query)
        books = result.scalars().all()
        return TypeAdapter(list[FullBookInfo]).validate_python(books)

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

    async def create_book(self, new_book: BookCreate) -> FullBookInfo:
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

        return await self._get_book_or_raise(book_id)

    async def _validate_ids_or_raise(self, model, ids, entity_name):
        result = await self._session.scalars(select(model.id).where(model.id.in_(ids)))
        existing_ids = set(result.all())
        missing_ids = set(ids) - existing_ids
        if missing_ids:
            raise NotFoundError(entity_name, missing_ids)

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
