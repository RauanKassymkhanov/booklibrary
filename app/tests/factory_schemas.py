from polyfactory.factories.pydantic_factory import ModelFactory
from app.api.authors.schemas import AuthorCreate
from app.api.books.schemas import BookCreate
from app.api.genres.schemas import GenreCreate


class GenreCreateFactory(ModelFactory[GenreCreate]):
    __model__ = GenreCreate


class AuthorCreateFactory(ModelFactory[AuthorCreate]):
    __model__ = AuthorCreate


class BookCreateFactory(ModelFactory[BookCreate]):
    __model__ = BookCreate
