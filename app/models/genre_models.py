from sqlalchemy.orm import relationship, Mapped
from app.models.base import Base, BooksGenres


class Genre(Base):
    __tablename__ = "genres"
    id: Mapped[Base.intpk]
    name: Mapped[Base.str32]

    books: Mapped[list["Book"]] = relationship("Book",secondary=BooksGenres, back_populates="genres")
