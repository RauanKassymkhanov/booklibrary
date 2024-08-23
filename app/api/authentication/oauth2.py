import jwt
from fastapi.security import OAuth2PasswordBearer

from app.api.exceptions import UnauthorizedException
from app.config import get_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def decode_token(token: str) -> id:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload["id"]
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Token has expired.")
    except jwt.InvalidTokenError:
        raise UnauthorizedException()
