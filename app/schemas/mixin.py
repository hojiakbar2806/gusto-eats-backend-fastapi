from enum import Enum
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    phone_number: int

class Roles(str, Enum):
    admin = "admin"
    user = "user"
