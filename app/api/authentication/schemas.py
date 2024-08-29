from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel


class TokenType(StrEnum):
    BEARER = "bearer"


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: TokenType


class TokenData(BaseModel):
    id: str


class DecodedToken(BaseModel):
    id: UUID
    exp: int
