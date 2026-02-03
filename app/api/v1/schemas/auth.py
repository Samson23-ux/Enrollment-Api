import enum
from pydantic import BaseModel, EmailStr


class TokenStatus(str, enum.Enum):
    VALID: str = "valid"
    REVOKED: str = "revoked"
    USED: str = "used"


class TokenDataV1(BaseModel):
    email: EmailStr


class TokenV1(BaseModel):
    access_token: str
    token_type: str = "bearer"
