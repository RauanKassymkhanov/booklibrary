from unittest.mock import patch
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.books.service import BookService
from app.api.exceptions import NotFoundError
from app.models import BookModel
from app.tests.factory_creators import create_test_book, create_test_author, create_test_genre
from app.tests.factory_schemas import BookCreateFactory


async def test_get_books(client: AsyncClient, session: AsyncSession) -> None:
    book = await create_test_book(session, title="Troy")

    response = await client.get("/books/")

    assert response.status_code == 200
    books = response.json()
    expected_book = book.model_dump()
    expected_book["published_date"] = expected_book["published_date"].strftime("%Y-%m-%d")
    assert [expected_book] == books


async def test_get_book(client: AsyncClient, session: AsyncSession) -> None:
    book = await create_test_book(session, title="book2")

    response = await client.get(f"/books/{book.id}")

    assert response.status_code == 200
    book_data = response.json()
    expected_book = book.model_dump()
    expected_book["published_date"] = expected_book["published_date"].strftime("%Y-%m-%d")
    assert expected_book == book_data


async def test_get_book_not_exist(client: AsyncClient, session: AsyncSession) -> None:
    response = await client.get("/books/88888")

    assert response.status_code == 404


async def test_create_book(client: AsyncClient, session: AsyncSession) -> None:
    author = await create_test_author(session, "author")
    genre = await create_test_genre(session, "genre")

    book_data = BookCreateFactory.build(session, title="book1", author_ids=[author.id], genre_ids=[genre.id])

    book_dict = book_data.model_dump()
    book_dict["published_date"] = book_dict["published_date"].isoformat()

    response = await client.post("/books/", json=book_dict)
    assert response.status_code == 201
    created_book = response.json()

    expected_book = {
        "id": created_book["id"],
        "title": book_data.title,
        "published_date": book_data.published_date.isoformat(),
        "description": book_data.description,
        "authors": [{"bio": author.bio, "id": author.id, "name": author.name}],
        "genres": [{"id": genre.id, "name": genre.name}],
    }

    assert created_book == expected_book


async def test_delete_book_success(client: AsyncClient, session: AsyncSession) -> None:
    book = await create_test_book(session, title="Book5")

    response = await client.delete(f"/books/{book.id}")

    assert response.status_code == 204


async def test_delete_book_non_exist(client: AsyncClient, session: AsyncSession) -> None:
    response = await client.delete("/books/8000000")

    assert response.status_code == 404


async def test_update_book(client: AsyncClient, session: AsyncSession) -> None:
    book = await create_test_book(session, title="book2")
    author = await create_test_author(session, name="author")
    genre = await create_test_genre(session, name="genre")

    updated_title = "updated title"
    updated_description = "updated description"
    updated_author_ids = [author.id]
    updated_genre_ids = [genre.id]
    updated_published_date = "2024-08-20"
    payload = {
        "title": updated_title,
        "author_ids": updated_author_ids,
        "genre_ids": updated_genre_ids,
        "published_date": updated_published_date,
        "description": updated_description,
    }
    response = await client.put(f"/books/{book.id}", json=payload)
    assert response.status_code == 200
    updated_book = response.json()

    expected_book = {
        "id": book.id,
        "title": updated_title,
        "published_date": updated_published_date,
        "description": updated_description,
        "authors": [{"bio": author.bio, "id": author.id, "name": author.name}],
        "genres": [{"id": genre.id, "name": genre.name}],
    }

    assert updated_book == expected_book


async def test_update_book_non_exist(client: AsyncClient, session: AsyncSession) -> None:
    book = BookCreateFactory.build(title="book2")
    book_dict = book.model_dump()
    book_dict["published_date"] = book_dict["published_date"].isoformat()
    response = await client.put("/books/8000000", json=book_dict)
    assert response.status_code == 404


async def test_create_book_transaction_rollback(session: AsyncSession) -> None:
    book_service = BookService(session)
    new_book = BookCreateFactory.build()

    with patch.object(book_service, "_validate_ids_or_raise", side_effect=NotFoundError("Author", {8000})):
        with pytest.raises(NotFoundError):
            await book_service.create_book(new_book)

    query = select(BookModel).where(BookModel.title == new_book.title)
    result = await session.execute(query)
    assert result.scalar() is None


async def test_create_book_non_exist_author_or_genre(client: AsyncClient, session: AsyncSession) -> None:
    book = BookCreateFactory.build(title="book2")
    book_dict = book.model_dump()
    book_dict["author_ids"] = [800000]
    book_dict["genre_ids"] = [800000]
    book_dict["published_date"] = book_dict["published_date"].isoformat()
    response = await client.post("/books/", json=book_dict)
    assert response.status_code == 404
