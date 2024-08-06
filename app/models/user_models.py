from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.models.base import Base
import uuid


class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    username: Mapped[Base.str32] = mapped_column(unique=True)
    email: Mapped[Base.str32] = mapped_column(unique=True)
    password_hash: Mapped[Base.str32]

    subscriptions: Mapped[list["Subscription"]] = relationship("Subscription", back_populates="users")