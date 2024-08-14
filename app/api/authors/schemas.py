from pydantic import BaseModel, ConfigDict, Field


class AuthorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=32)
    bio: str


class AuthorCreate(AuthorBase):
    pass


class Author(AuthorBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
