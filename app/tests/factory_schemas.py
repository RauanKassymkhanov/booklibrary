from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import EmailStr

from app.api.authors.schemas import AuthorCreate
from app.api.books.schemas import BookCreate
from app.api.genres.schemas import GenreCreate
from app.api.users.schemas import UserCreate, UserUpdate, UserUpdatePassword
from faker import Faker

fake = Faker()


class GenreCreateFactory(ModelFactory[GenreCreate]):
    __model__ = GenreCreate


class AuthorCreateFactory(ModelFactory[AuthorCreate]):
    __model__ = AuthorCreate


class BookCreateFactory(ModelFactory[BookCreate]):
    __model__ = BookCreate


class UserCreateFactory(ModelFactory[UserCreate]):
    __model__ = UserCreate

    @classmethod
    def email(cls) -> EmailStr:
        return fake.email()

    @classmethod
    def password(cls) -> str:
        return "password123"


class UserUpdateFactory(ModelFactory[UserUpdate]):
    __model__ = UserUpdate

    @classmethod
    def email(cls) -> EmailStr:
        return "rauan@gmail.com"


class UserUpdatePasswordFactory(ModelFactory[UserUpdatePassword]):
    __model__ = UserUpdatePassword

    @classmethod
    def current_password(cls) -> str:
        return "password123"

    @classmethod
    def new_password(cls) -> str:
        return "Rauan12345"

    @classmethod
    def confirm_new_password(cls) -> str:
        return "Rauan12345"
