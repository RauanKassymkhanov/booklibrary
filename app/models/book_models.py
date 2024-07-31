from sqlalchemy import Date, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.models.base import Base, BooksGenres, BooksAuthors


class Book(Base):
    __tablename__ = "books"
    id: Mapped[Base.intpk]
    title: Mapped[Base.str32]
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id", ondelete="CASCADE"))
    published_date: Mapped[Date] = mapped_column(Date)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id", ondelete="CASCADE"))
    description: Mapped[str] = mapped_column(Text)

    authors: Mapped[list["Author"]] = relationship("Author", secondary=BooksAuthors, back_populates="books")
    genres: Mapped[list["Genre"]] = relationship("Genre",secondary=BooksGenres, back_populates="books")
