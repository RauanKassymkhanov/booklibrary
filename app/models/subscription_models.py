from sqlalchemy import Date, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.models.base import Base
import uuid


class Subscription(Base):
    __tablename__ = "subscriptions"
    id: Mapped[Base.intpk]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id", ondelete="CASCADE"))
    subscribed_date: Mapped[Date] = mapped_column(Date)

    users: Mapped["User"] = relationship("User", back_populates="subscriptions")
    authors: Mapped["Author"] = relationship("Author", back_populates="subscriptions")
