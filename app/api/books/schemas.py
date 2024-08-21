from pydantic import BaseModel, Field, ConfigDict
from datetime import date

from app.api.authors.schemas import Author
from app.api.genres.schemas import Genre


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=32)
    published_date: date
    description: str

    model_config = ConfigDict(from_attributes=True)


class BookCreate(BookBase):
    author_ids: list[int]
    genre_ids: list[int]


class Book(BookBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class FullBookInfo(BookBase):
    id: int
    authors: list[Author]
    genres: list[Genre]

    model_config = ConfigDict(from_attributes=True)
