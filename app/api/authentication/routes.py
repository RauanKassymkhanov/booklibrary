from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from app.api.authentication.oauth2 import oauth2_scheme
from app.api.authentication.schemas import Token
from app.api.authentication.service import UserLoginService
from app.api.users.schemas import User
from app.api.exceptions import UnauthorizedException

router = APIRouter(tags=["authentication"])


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    token_service: UserLoginService = Depends(),
):
    try:
        return await token_service.login_for_access_token(form_data.username, form_data.password)
    except UnauthorizedException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_token: Annotated[str, Depends(oauth2_scheme)],
    token_service: UserLoginService = Depends(),
):
    try:
        return await token_service.refresh_access_token(refresh_token)
    except UnauthorizedException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=User)
async def read_users_me(
    token: str = Depends(oauth2_scheme),
    token_service: UserLoginService = Depends(),
):
    try:
        return await token_service.get_current_user(token)
    except UnauthorizedException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
