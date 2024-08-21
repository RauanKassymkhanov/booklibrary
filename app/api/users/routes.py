from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from app.api.exceptions import (
    NotFoundError,
    UsernameAlreadyExistsException,
    EmailAlreadyExistsException,
    PasswordException,
)
from app.api.users.schemas import User, UserCreate, UserUpdate, UserUpdatePassword
from app.api.users.service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[User])
async def get_books(service: UserService = Depends()):
    return await service.get_users()


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: UUID, service: UserService = Depends()):
    try:
        return await service.get_user(user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(new_user: UserCreate, service: UserService = Depends()):
    try:
        user_created = await service.create_user(new_user)
    except (UsernameAlreadyExistsException, EmailAlreadyExistsException) as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return user_created


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, service: UserService = Depends()):
    try:
        await service.delete_user(user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{user_id}", response_model=User)
async def update_user(user_id: UUID, updated_user: UserUpdate, service: UserService = Depends()):
    try:
        return await service.update_user(user_id, updated_user)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (UsernameAlreadyExistsException, EmailAlreadyExistsException) as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.put("/{user_id}/change_password", response_model=User)
async def update_user_password(
    user_id: UUID, updated_user_password: UserUpdatePassword, service: UserService = Depends()
):
    try:
        return await service.update_user_password(user_id, updated_user_password)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (UsernameAlreadyExistsException, EmailAlreadyExistsException) as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except PasswordException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
