from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from typing import Annotated


class Base(DeclarativeBase):
    str32 = Annotated[str, mapped_column(String(32))]
    intpk = Annotated[int, mapped_column(primary_key=True)]


class BooksAuthors(Base):
    __tablename__ = "books_authors"

    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"), primary_key=True)


class BooksGenres(Base):
    __tablename__ = "books_genres"

    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), primary_key=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"), primary_key=True)
