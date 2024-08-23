from typing_extensions import Self
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_serializer, model_validator


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=32)
    email: EmailStr = Field(min_length=8, max_length=32)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=32)


class UserUpdate(UserBase):
    username: str = Field(min_length=1, max_length=32)
    email: EmailStr = Field(min_length=8, max_length=32)


class UserUpdatePassword(BaseModel):
    current_password: str = Field(min_length=8, max_length=32)
    new_password: str = Field(min_length=8, max_length=32)
    confirm_new_password: str = Field(min_length=8, max_length=32)

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.new_password and self.confirm_new_password and self.new_password != self.confirm_new_password:
            raise ValueError("The new passwords do not match.")
        return self


class User(UserBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("id")
    def serialize_id(self, _id: UUID) -> str:
        return str(_id)
