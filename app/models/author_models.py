from sqlalchemy import Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.models.base import Base, BooksAuthors


class Author(Base):
    __tablename__ = "authors"
    id: Mapped[Base.intpk]
    name: Mapped[Base.str32]
    bio: Mapped[str] = mapped_column(Text)

    books: Mapped[list["Book"]] = relationship("Book", secondary=BooksAuthors, back_populates="authors")
    subscriptions: Mapped[list["Subscription"]] = relationship("Subscription", back_populates="authors")
