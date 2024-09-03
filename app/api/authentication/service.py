from datetime import timedelta, datetime, timezone
import jwt
from jwt import InvalidTokenError
from sqlalchemy import select
from app.api.base_service import BaseService
from app.api.authentication.oauth2 import decode_token
from app.api.authentication.schemas import Token, TokenType, TokenData
from app.api.exceptions import UnauthorizedException
from app.api.utils import verify_password
from app.config import get_settings
from app.models import UserModel


def create_access_token(data: TokenData) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.model_dump()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: TokenData) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.model_dump()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


class UserLoginService(BaseService):
    async def authenticate_user(self, username: str, password: str) -> UserModel:
        query = select(UserModel).where(UserModel.username == username)
        result = await self._session.execute(query)
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedException("Incorrect username or password")

        return user

    async def login_for_access_token(self, username: str, password: str) -> Token:
        user = await self.authenticate_user(username, password)

        access_token = create_access_token(data=TokenData(id=str(user.id)))

        refresh_token = create_refresh_token(data=TokenData(id=str(user.id)))

        return Token(access_token=access_token, refresh_token=refresh_token, token_type=TokenType.BEARER)

    async def refresh_access_token(self, refresh_token: str) -> Token:
        try:
            decoded_token = decode_token(refresh_token)
            user_id = decoded_token.id
        except InvalidTokenError:
            raise UnauthorizedException

        access_token = create_access_token(data=TokenData(id=str(user_id)))
        refresh_token = create_refresh_token(data=TokenData(id=str(user_id)))

        return Token(access_token=access_token, refresh_token=refresh_token, token_type=TokenType.BEARER)
