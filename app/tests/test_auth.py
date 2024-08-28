import jwt
from httpx import AsyncClient
from freezegun import freeze_time
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.authentication.schemas import TokenData
from app.api.authentication.service import create_access_token, create_refresh_token
from app.config import get_settings
from app.tests.factory_creators import create_test_user


async def test_login_success(client: AsyncClient, session: AsyncSession):
    login_data = await create_test_user(session, username="testuser")

    response = await client.post("/login", data={"username": login_data.username, "password": "password123"})

    assert response.status_code == 200
    assert "access_token", "refresh_token" in response.json()


async def test_login_invalid_credentials(client: AsyncClient, session: AsyncSession):
    user = await create_test_user(session, username="testuser")

    response = await client.post("/login", data={"username": user.username, "password": "wrongpassword"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}


async def test_access_with_valid_token(client: AsyncClient, session: AsyncSession):
    settings = get_settings()
    user = await create_test_user(session, username="testuser")

    access_token = create_access_token(data=TokenData(id=str(user.id)))

    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/me", headers=headers)

    assert response.status_code == 200
    decoded_token = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded_token["id"] == str(user.id)


async def test_access_with_expired_token(client: AsyncClient, session: AsyncSession):
    user = await create_test_user(session, username="testuser")
    access_token = create_access_token(data=TokenData(id=str(user.id)))
    with freeze_time(datetime.now(timezone.utc) + timedelta(minutes=31)):
        headers = {"Authorization": f"Bearer {access_token}"}

        response = await client.get("/me", headers=headers)

    assert response.status_code == 401
    assert response.json() == {"detail": "Token has expired."}


async def test_access_with_invalid_token(client: AsyncClient):
    invalid_token = "invalid.token.value"
    headers = {"Authorization": f"Bearer {invalid_token}"}

    response = await client.get("/me", headers=headers)

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials."}


async def test_refresh_token(client: AsyncClient, session: AsyncSession):
    settings = get_settings()
    user = await create_test_user(session, username="testuser")

    refresh_token = create_refresh_token(data=TokenData(id=str(user.id)))

    response = await client.post("/refresh", headers={"Authorization": f"Bearer {refresh_token}"})

    assert response.status_code == 200
    decoded_token = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded_token["id"] == str(user.id)
