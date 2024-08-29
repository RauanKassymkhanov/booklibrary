from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SubscriptionBase(BaseModel):
    author_id: int


class SubscriptionCreate(SubscriptionBase):
    pass


class Subscription(SubscriptionBase):
    user_id: UUID
    subscription_date: datetime

    model_config = ConfigDict(from_attributes=True)


class SubscriptionResponse(BaseModel):
    detail: str
