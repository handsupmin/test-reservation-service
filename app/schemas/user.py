from enum import Enum

from pydantic import BaseModel


class UserType(str, Enum):
    admin = "admin"
    user = "user"


class UserInfo(BaseModel):
    idx: int
    type: UserType
