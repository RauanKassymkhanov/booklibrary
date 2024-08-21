from sqlalchemy.orm import relationship, Mapped
from app.database import Base
from app.models.base import BooksGenres
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.books import BookModel


class GenreModel(Base):
    __tablename__ = "genres"
    id: Mapped[Base.intpk]
    name: Mapped[Base.str32]

    books: Mapped[list["BookModel"]] = relationship(
        "BookModel", secondary=BooksGenres.__tablename__, back_populates="genres"
    )
