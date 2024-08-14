import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.factory_creators import create_test_author


async def test_get_authors(client: AsyncClient, session: AsyncSession) -> None:
    author = await create_test_author(session, 'author1')

    response = await client.get("/authors/")

    assert response.status_code == 200
    authors = response.json()
    author_names = [g["name"] for g in authors]
    assert author.name in author_names


async def test_get_author(client: AsyncClient, session: AsyncSession) -> None:
    author = await create_test_author(session, "author2")

    response = await client.get(f"/authors/{author.id}")

    assert response.status_code == 200
    author_data = response.json()
    assert author_data["name"] == author.name


async def test_get_author_not_exist(client: AsyncClient, session: AsyncSession) -> None:
    response = await client.get("/authors/88888")

    assert response.status_code == 404


@pytest.mark.parametrize("name", ["author1","author2","author3"])
async def test_create_author(client: AsyncClient, session: AsyncSession, name: str) -> None:
    response = await client.post("/authors/", json={"name": name, "bio": "bio"})

    assert response.status_code == 201
    created_author = response.json()
    assert (created_author["name"], created_author["bio"]) == (name, "bio")


async def test_delete_author_success(client: AsyncClient, session: AsyncSession) -> None:
    author = await create_test_author(session, "author4")

    response = await client.delete(f"/authors/{author.id}")

    assert response.status_code == 204


async def test_delete_author_non_exist(client: AsyncClient, session: AsyncSession) -> None:
    response = await client.delete("/authors/8000000")

    assert response.status_code == 404


async def test_update_author(client: AsyncClient, session: AsyncSession) -> None:
    author = await create_test_author(session, "author5")
    updated_name = "updated author"
    updated_bio = "updated bio"

    response = await client.put(f"/authors/{author.id}", json={"name": updated_name, "bio": updated_bio})

    assert response.status_code == 200
    updated_author = response.json()
    assert (updated_author["name"], updated_author["bio"]) == (updated_name, updated_bio)


async def test_update_author_non_exist(client: AsyncClient, session: AsyncSession) -> None:
    updated_name = "updated author"
    updated_bio = "updated bio"

    response = await client.put("/authors/8000000", json={"name": updated_name, "bio": updated_bio})

    assert response.status_code == 404
