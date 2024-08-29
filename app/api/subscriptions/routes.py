from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from starlette import status
from app.api.authentication.oauth2 import get_current_user
from app.api.exceptions import NotFoundError, AlreadySubscribedError, UnauthorizedException, AlreadyUnsubscribedError
from app.api.subscriptions.schemas import SubscriptionCreate, SubscriptionResponse
from app.api.subscriptions.service import SubscriptionService
from app.models import UserModel

router = APIRouter(tags=["subscriptions"])


@router.post("/subscribe/", status_code=status.HTTP_201_CREATED, response_model=SubscriptionResponse)
async def subscribe_to_author(
    subscription: SubscriptionCreate,
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(get_current_user),
    service: SubscriptionService = Depends(),
):
    try:
        await service.subscribe_to_author(current_user.id, subscription, background_tasks)
        return {"detail": "Subscribed successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except AlreadySubscribedError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)


@router.delete("/unsubscribe/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unsubscribe_from_author(
    author_id: int,
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(get_current_user),
    service: SubscriptionService = Depends(),
):
    try:
        await service.unsubscribe_from_author(current_user.id, author_id, background_tasks)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)
    except AlreadyUnsubscribedError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
