from typing import Annotated
import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.authentication.schemas import DecodedToken
from app.api.exceptions import UnauthorizedException
from app.api.users.schemas import User
from app.config import get_settings
from app.database import get_session
from app.models import UserModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def decode_token(token: str) -> DecodedToken:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        decoded_token = DecodedToken(**payload)
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Token has expired.")
    except jwt.InvalidTokenError:
        raise UnauthorizedException("Invalid Token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: AsyncSession = Depends(get_session)
) -> User:
    try:
        decoded_token = decode_token(token)
        user_id = decoded_token.id
    except InvalidTokenError:
        raise UnauthorizedException

    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    return User(id=user.id, username=user.username, email=user.email)
