import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.tests.factory_creators import create_test_user
from app.tests.factory_schemas import UserCreateFactory, UserUpdateFactory, UserUpdatePasswordFactory


async def test_get_users(client: AsyncClient, session: AsyncSession) -> None:
    user = await create_test_user(session, "username")
    response = await client.get("/users/")
    assert response.status_code == 200
    users = response.json()
    expected_user = user.model_dump()
    assert [expected_user] == users


async def test_get_user(client: AsyncClient, session) -> None:
    user = await create_test_user(session, "username")
    response = await client.get(f"/users/{user.id}")
    assert response.status_code == 200
    user_data = response.json()
    expected_user = user.model_dump()
    assert expected_user == user_data


async def test_get_user_not_exist(client: AsyncClient, session: AsyncSession) -> None:
    response = await client.get(f"/users/{str(uuid.uuid4())}")

    assert response.status_code == 404


async def test_create_user(client: AsyncClient, session: AsyncSession) -> None:
    user = UserCreateFactory.build(username="username")
    user_dict = user.model_dump()
    response = await client.post("/users/", json=user_dict)
    assert response.status_code == 201
    user_data = response.json()

    expected_user = {
        "id": user_data["id"],
        "username": user.username,
        "email": user.email,
    }

    assert expected_user == user_data


async def test_create_user_username_taken(client: AsyncClient, session: AsyncSession) -> None:
    user = await create_test_user(session, "username")
    payload = {"username": user.username, "email": "email@gmail.com", "password": "stringst"}
    response = await client.post("/users/", json=payload)

    assert response.status_code == 409


async def test_create_user_email_taken(client: AsyncClient, session: AsyncSession) -> None:
    user = await create_test_user(session, "username")
    payload = {"username": "username1", "email": user.email, "password": "stringst"}
    response = await client.post("/users/", json=payload)

    assert response.status_code == 409


async def test_delete_user_success(client: AsyncClient, session: AsyncSession) -> None:
    user = await create_test_user(session, "username")

    response = await client.delete(f"/users/{user.id}")

    assert response.status_code == 204


async def test_delete_user_not_exist(client: AsyncClient, session: AsyncSession) -> None:
    response = await client.delete(f"/users/{str(uuid.uuid4())}")

    assert response.status_code == 404


async def test_update_user(client: AsyncClient, session: AsyncSession) -> None:
    user = await create_test_user(session, "username")
    user_update = UserUpdateFactory.build(username="username5")
    user_dict = user_update.model_dump()

    response = await client.put(f"/users/{user.id}", json=user_dict)
    assert response.status_code == 200
    updated_user = response.json()

    expected_user = {
        "id": str(user.id),
        "username": user_update.username,
        "email": user_update.email,
    }

    assert expected_user == updated_user


async def test_update_user_non_exist(client: AsyncClient, session: AsyncSession) -> None:
    user = UserUpdateFactory.build(username="username")

    user_dict = user.model_dump()
    response = await client.put(f"/users/{str(uuid.uuid4())}", json=user_dict)
    assert response.status_code == 404


async def test_update_user_username_taken(client: AsyncClient, session: AsyncSession) -> None:
    await create_test_user(session, "username2")
    user = await create_test_user(session, "username")
    user_update = UserUpdateFactory.build(username="username2")
    user_dict = user_update.model_dump()

    response = await client.put(f"/users/{user.id}", json=user_dict)

    assert response.status_code == 409
    assert response.json() == {"detail": f"Username '{user_update.username}' is already taken."}


async def test_update_user_email_taken(client: AsyncClient, session: AsyncSession) -> None:
    user1 = await create_test_user(session, "username")
    user = await create_test_user(session, "username2")
    user_update = UserUpdateFactory.build(username="username2")
    user_dict = user_update.model_dump()
    user_dict["email"] = user1.email

    response = await client.put(f"/users/{user.id}", json=user_dict)

    assert response.status_code == 409
    assert response.json() == {"detail": f"Email '{user1.email}' is already taken."}


async def test_update_user_password(client: AsyncClient, session: AsyncSession) -> None:
    user = await create_test_user(session, "username")
    user_update = UserUpdatePasswordFactory.build(username="username5")
    user_dict = user_update.model_dump()

    response = await client.put(f"/users/{user.id}/change_password", json=user_dict)
    assert response.status_code == 200


async def test_update_user_wrong_current_password(client: AsyncClient, session: AsyncSession) -> None:
    user = await create_test_user(session, "username")
    user_update = UserUpdatePasswordFactory.build(username="username5")
    user_dict = user_update.model_dump()
    user_dict["current_password"] = "123456789"

    response = await client.put(f"/users/{user.id}/change_password", json=user_dict)

    assert response.status_code == 400
    assert response.json() == {"detail": "Current password is incorrect."}


async def test_update_user_wrong_password_confirmation(client: AsyncClient, session: AsyncSession) -> None:
    user = await create_test_user(session, "username")
    user_update = UserUpdatePasswordFactory.build(username="username5")
    user_dict = user_update.model_dump()
    user_dict["confirm_new_password"] = "qwerty123456"

    response = await client.put(f"/users/{user.id}/change_password", json=user_dict)

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Value error, The new passwords do not match."
