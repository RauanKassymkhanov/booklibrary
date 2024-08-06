from sqlalchemy import Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base
from app.models.base import BooksAuthors


class AuthorModel(Base):
    __tablename__ = "authors"
    id: Mapped[Base.intpk]
    name: Mapped[Base.str32]
    bio: Mapped[str] = mapped_column(Text)

    books: Mapped[list["BookModel"]] = relationship("BookModel", secondary=BooksAuthors.__tablename__, back_populates="authors")
    subscriptions: Mapped[list["SubscriptionModel"]] = relationship("SubscriptionModel", back_populates="authors")
