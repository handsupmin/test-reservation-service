import enum

from sqlalchemy import Column, Integer, Enum, DateTime, String

from app.db.base import Base


class UserType(enum.Enum):
    admin = "admin"
    user = "user"


class TokenInfo(Base):
    __tablename__ = "token_info"

    user_idx = Column(Integer, nullable=False)
    user_type = Column(Enum(UserType), nullable=False)
    token = Column(String, nullable=False)
    expired_at = Column(DateTime, nullable=False)
