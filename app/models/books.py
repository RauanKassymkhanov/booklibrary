from sqlalchemy import Date, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.models.base import BooksGenres, BooksAuthors
from app.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.authors import AuthorModel
    from app.models.genres import GenreModel


class BookModel(Base):
    __tablename__ = "books"
    id: Mapped[Base.intpk]
    title: Mapped[Base.str32]
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id", ondelete="CASCADE"))
    published_date: Mapped[Date] = mapped_column(Date)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id", ondelete="CASCADE"))
    description: Mapped[str] = mapped_column(Text)

    authors: Mapped[list["AuthorModel"]] = relationship("AuthorModel", secondary=BooksAuthors.__tablename__,
                                                        back_populates="books")
    genres: Mapped[list["GenreModel"]] = relationship("GenreModel", secondary=BooksGenres.__tablename__,
                                                      back_populates="books")
