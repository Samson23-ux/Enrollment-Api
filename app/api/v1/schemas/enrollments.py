from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class EnrollmentBaseV1(BaseModel):
    course_title: str
    course_code: str
    course_duration: int
    created_at: datetime


class ResponseBase(BaseModel):
    message: str


class EnrollmentReadV1(EnrollmentBaseV1):
    pass


class EnrollmentResponseV1(ResponseBase):
    data: Optional[EnrollmentReadV1 | list[EnrollmentReadV1]] = None
