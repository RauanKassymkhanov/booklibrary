from datetime import datetime
from uuid import UUID
from fastapi import BackgroundTasks, Depends
from sqlalchemy import insert, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authors.schemas import Author
from app.api.base_service import BaseService
from app.api.exceptions import NotFoundError, AlreadySubscribedError, AlreadyUnsubscribedError
from app.api.subscriptions.email_service import EmailService
from app.api.subscriptions.schemas import SubscriptionCreate
from app.database import get_session
from app.models import AuthorModel, SubscriptionModel, UserModel


class SubscriptionService(BaseService):
    def __init__(self, email_service: EmailService = Depends(), session: AsyncSession = Depends(get_session)):
        super().__init__(session)
        self.email_service = email_service

    async def subscribe_to_author(
        self, user_id: UUID, subscription: SubscriptionCreate, background_tasks: BackgroundTasks
    ) -> None:
        author = await self._validate_author_or_raise(subscription.author_id)
        await self._check_already_subscribed_or_raise(user_id, subscription.author_id)

        subscription_query = (
            insert(SubscriptionModel)
            .values(user_id=user_id, author_id=subscription.author_id, subscribed_date=datetime.now())
            .returning(SubscriptionModel)
        )

        await self._session.execute(subscription_query)

        user_query = select(UserModel).where(UserModel.id == user_id)
        user = await self._session.scalar(user_query)
        background_tasks.add_task(
            self.email_service.send_email,
            to_email=user.email,
            subject="Subscription Confirmation",
            message=f"Dear {user.username},\n\nYou have successfully subscribed to {author.name}."
            f"\n\nAuthor Bio: {author.bio}\n\nThank you!",
        )

    async def unsubscribe_from_author(self, user_id: UUID, author_id: int, background_tasks: BackgroundTasks) -> None:
        await self._validate_author_or_raise(author_id)
        user_query = select(UserModel).where(UserModel.id == user_id)
        author_query = select(AuthorModel).where(AuthorModel.id == author_id)

        user = await self._session.scalar(user_query)
        author = await self._session.scalar(author_query)

        delete_query = delete(SubscriptionModel).where(
            SubscriptionModel.user_id == user_id, SubscriptionModel.author_id == author_id
        )
        result = await self._session.execute(delete_query)

        if result.rowcount == 0:
            raise AlreadyUnsubscribedError(author_id)

        background_tasks.add_task(
            self.email_service.send_email,
            to_email=user.email,
            subject="Unsubscription Confirmation",
            message=f"Dear {user.username},\n\nYou have successfully unsubscribed from {author.name}."
            f"\n\nIf this was a mistake, you can always re-subscribe.\n\nThank you!",
        )

    async def _validate_author_or_raise(self, author_id: int) -> Author:
        query = select(AuthorModel).where(AuthorModel.id == author_id)

        author = await self._session.scalar(query)
        if not author:
            raise NotFoundError("Author", author_id)
        return Author.model_validate(author)

    async def _check_already_subscribed_or_raise(self, user_id: UUID, author_id: int) -> None:
        existing_subscription = await self._session.execute(
            select(SubscriptionModel).where(
                SubscriptionModel.user_id == user_id, SubscriptionModel.author_id == author_id
            )
        )
        if existing_subscription.scalars().first():
            raise AlreadySubscribedError(author_id)
