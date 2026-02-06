from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CourseBaseV1(BaseModel):
    title: str = Field(min_length=5)
    description: str = Field(min_length=10, max_length=50)
    code: str = Field(min_length=3)
    instructor: str = Field(min_length=8)
    capacity: int = Field(min_length=10)
    duration: int


class ResponseBase(BaseModel):
    message: str


class CourseCreateV1(CourseBaseV1):
    pass

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class CourseReadV1(CourseBaseV1):
    id: UUID
    is_active: bool
    total_students: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseUpdateV1(BaseModel):
    title: Optional[str] = Field(default=None, min_length=5)
    description: Optional[str] = Field(default=None, min_length=10, max_length=50)
    code: Optional[str] = Field(default=None, min_length=3)
    instructor: Optional[str] = Field(default=None, min_length=8)
    capacity: Optional[int] = Field(default=None, min_length=10)
    duration: Optional[int] = None


class CourseResponseV1(ResponseBase):
    data: CourseReadV1 | list[CourseReadV1]
