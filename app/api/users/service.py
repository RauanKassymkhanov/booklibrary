from uuid import UUID
from pydantic import TypeAdapter
from sqlalchemy import select, insert, delete, update, or_
from app.api.base_service import BaseService
from app.api.exceptions import (
    NotFoundError,
    EmailAlreadyExistsException,
    UsernameAlreadyExistsException,
    PasswordException,
)
from app.api.users.schemas import User, UserCreate, UserUpdate, UserUpdatePassword
from app.models import UserModel
from app.api.users.utils import get_password_hash, verify_password


class UserService(BaseService):
    async def get_users(self) -> list[User]:
        query = select(UserModel)
        result = await self._session.execute(query)
        users = result.scalars().all()
        return TypeAdapter(list[User]).validate_python(users)

    async def _get_user_or_raise(self, user_id: UUID) -> User:
        query = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            raise NotFoundError("User", user_id)
        return User.model_validate(user)

    async def create_user(self, new_user: UserCreate) -> User:
        await self._check_for_existing_user(new_user.username, new_user.email)

        hashed_password = get_password_hash(new_user.password)
        new_user_data = new_user.model_dump(exclude={"password"})

        query = insert(UserModel).values(**new_user_data, password_hash=hashed_password).returning(UserModel)
        result = await self._session.execute(query)
        created_user = result.scalar_one()
        return User.model_validate(created_user)

    async def get_user(self, user_id: UUID) -> User:
        return await self._get_user_or_raise(user_id)

    async def delete_user(self, user_id: UUID) -> None:
        await self._get_user_or_raise(user_id)
        delete_query = delete(UserModel).where(UserModel.id == user_id)
        await self._session.execute(delete_query)

    async def update_user(self, user_id: UUID, updated_user: UserUpdate) -> User:
        await self._get_user_or_raise(user_id)
        await self._check_for_existing_user(updated_user.username, updated_user.email, user_id)

        update_query = (
            update(UserModel).values(**updated_user.model_dump()).where(UserModel.id == user_id).returning(UserModel)
        )
        result = await self._session.execute(update_query)
        updated_user = result.scalar_one()

        return User.model_validate(updated_user)

    async def update_user_password(self, user_id: UUID, updated_user: UserUpdatePassword) -> User:
        existing_user_query = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(existing_user_query)
        existing_user = result.scalar_one_or_none()

        if not verify_password(updated_user.current_password, existing_user.password_hash):
            raise PasswordException("Current password is incorrect.")

        hashed_password = get_password_hash(updated_user.new_password)
        update_data = updated_user.model_dump(exclude={"current_password", "new_password", "confirm_new_password"})

        update_query = (
            update(UserModel)
            .values(**update_data, password_hash=hashed_password)
            .where(UserModel.id == user_id)
            .returning(UserModel)
        )
        result = await self._session.execute(update_query)
        updated_user = result.scalar_one()

        return User.model_validate(updated_user)

    async def _check_existing_user(self, username: str, email: str, exclude_user_id: UUID = None) -> User:
        query = select(UserModel).where(or_(UserModel.username == username, UserModel.email == email))

        if exclude_user_id:
            query = query.where(UserModel.id != exclude_user_id)

        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def _check_for_existing_user(self, username: str, email: str, user_id: UUID = None) -> None:
        existing_user = await self._check_existing_user(username, email, user_id)

        if existing_user:
            if existing_user.username == username:
                raise UsernameAlreadyExistsException(username)
            if existing_user.email == email:
                raise EmailAlreadyExistsException(email)
