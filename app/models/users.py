from sqlalchemy import String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.subscriptions import SubscriptionModel


class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[Base.str32] = mapped_column(unique=True)
    email: Mapped[Base.str32] = mapped_column(unique=True)
    password_hash: Mapped[str] = mapped_column(String(64))

    subscriptions: Mapped[list["SubscriptionModel"]] = relationship("SubscriptionModel", back_populates="users")
