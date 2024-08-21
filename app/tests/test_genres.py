import pytest
from httpx import AsyncClient
from app.tests.factory_creators import create_test_genre


async def test_get_genres(client: AsyncClient, session) -> None:
    genre = await create_test_genre(session, "Comedy")
    response = await client.get("/genres/")
    assert response.status_code == 200
    genres = response.json()
    assert any(g["name"] == genre.name for g in genres)


async def test_get_genre(client: AsyncClient, session) -> None:
    genre = await create_test_genre(session, "Science Fiction")
    response = await client.get(f"/genres/{genre.id}")
    assert response.status_code == 200
    assert response.json()["name"] == genre.name


async def test_get_genre_not_exist(client: AsyncClient, session) -> None:
    response = await client.get("/genres/88888")
    assert response.status_code == 404


@pytest.mark.parametrize("name", ["Fantasy", "Horror", "Romance"])
async def test_create_genre(client: AsyncClient, session, name: str) -> None:
    response = await client.post("/genres/", json={"name": name})
    assert response.status_code == 201
    created_genre = response.json()
    assert created_genre["name"] == name


async def test_delete_genre_success(client: AsyncClient, session) -> None:
    genre = await create_test_genre(session, "Thriller")
    response = await client.delete(f"/genres/{genre.id}")
    assert response.status_code == 204


async def test_delete_genre_non_exist(client: AsyncClient, session) -> None:
    response = await client.delete("/genres/8000000")
    assert response.status_code == 404


async def test_update_genre(client: AsyncClient, session) -> None:
    genre = await create_test_genre(session, "Drama")
    updated_name = "Updated Drama"
    response = await client.put(f"/genres/{genre.id}", json={"name": updated_name})
    assert response.status_code == 200
    updated_genre = response.json()
    assert updated_genre["name"] == updated_name


async def test_update_genre_non_exist(client: AsyncClient, session) -> None:
    updated_name = "Updated Genre"
    response = await client.put("/genres/8000000", json={"name": updated_name})
    assert response.status_code == 404
