from sqlalchemy import Date, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base
import uuid


class SubscriptionModel(Base):
    __tablename__ = "subscriptions"
    id: Mapped[Base.intpk]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id", ondelete="CASCADE"))
    subscribed_date: Mapped[Date] = mapped_column(Date)

    users: Mapped["UserModel"] = relationship("UserModel", back_populates="subscriptions")
    authors: Mapped["AuthorModel"] = relationship("AuthorModel", back_populates="subscriptions")
