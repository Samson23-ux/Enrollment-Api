import enum
from uuid import UUID
from pydantic import BaseModel


class TokenStatus(str, enum.Enum):
    VALID: str = "valid"
    REVOKED: str = "revoked"
    USED: str = "used"


class TokenDataV1(BaseModel):
    id: UUID


class TokenV1(BaseModel):
    access_token: str
    token_type: str = "bearer"
