import enum
from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STUDENT = "student"
    INSTRUCTOR = "instructor"


class UserBaseV1(BaseModel):
    name: str = Field(min_length=8, max_length=20)
    email: EmailStr
    nationality: str


    @field_validator("email", mode="after")
    @classmethod
    def email_to_lower(cls, v: EmailStr):
        return v.lower()


class ResponseBase(BaseModel):
    message: str


class UserCreateV1(UserBaseV1):
    password: str = Field(min_length=8)


    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class UserUpdateV1(BaseModel):
    name: Optional[str] = Field(default=None, min_length=8, max_length=20)
    email: Optional[EmailStr] = None
    nationality: Optional[str] = None


    @field_validator("email", mode="after")
    @classmethod
    def email_to_lower(cls, v: EmailStr):
        return v.lower()

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class UserReadV1(UserBaseV1):
    id: UUID
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserResponseV1(ResponseBase):
    data: UserReadV1 | list[UserReadV1]
