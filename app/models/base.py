from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from app.database import Base


class BooksAuthors(Base):
    __tablename__ = "books_authors"

    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True)


class BooksGenres(Base):
    __tablename__ = "books_genres"

    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), primary_key=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True)
