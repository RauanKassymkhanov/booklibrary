from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.authentication.schemas import TokenData
from app.api.authentication.service import create_access_token
from app.tests.factory_creators import create_test_author, create_test_user, subscribe_user_to_author


@patch("app.api.subscriptions.email_service.EmailService.send_email", new_callable=AsyncMock)
async def test_subscribe_to_author(mock_send_email, client: AsyncClient, session: AsyncSession) -> None:
    author = await create_test_author(session, name="author")
    user = await create_test_user(session, username="testuser")
    access_token = create_access_token(data=TokenData(id=str(user.id)))
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await client.post("/subscribe/", json={"author_id": author.id}, headers=headers)

    assert response.status_code == 201
    assert response.json() == {"detail": "Subscribed successfully"}

    mock_send_email.assert_called_once_with(
        to_email=user.email,
        subject="Subscription Confirmation",
        message=f"Dear {user.username},\n\nYou have successfully subscribed to author.\n\nAuthor Bio: {author.bio}\n"
        f"\nThank you!",
    )


@patch("app.api.subscriptions.email_service.EmailService.send_email", new_callable=AsyncMock)
async def test_unsubscribe_from_author(mock_send_email, client: AsyncClient, session: AsyncSession) -> None:
    author = await create_test_author(session, name="author")
    user = await create_test_user(session, username="testuser")
    await subscribe_user_to_author(session, user_id=user.id, author_id=author.id)

    access_token = create_access_token(data=TokenData(id=str(user.id)))
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await client.delete(f"/unsubscribe/{author.id}", headers=headers)

    assert response.status_code == 204

    mock_send_email.assert_called_once_with(
        to_email=user.email,
        subject="Unsubscription Confirmation",
        message=f"Dear {user.username},\n\nYou have successfully unsubscribed from {author.name}."
        f"\n\nIf this was a mistake, you can always re-subscribe.\n\nThank you!",
    )
