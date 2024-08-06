from polyfactory.factories.pydantic_factory import ModelFactory
from app.api.genres.schemas import GenreCreate


class GenreCreateFactory(ModelFactory[GenreCreate]):
    __model__ = GenreCreate
