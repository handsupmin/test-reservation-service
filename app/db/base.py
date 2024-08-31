from datetime import datetime

from sqlalchemy import create_engine, Column, DateTime, Integer
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.inspection import inspect

from app.core.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)


@as_declarative()
class Base:
    idx = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    __name__: str


def to_dict(obj):
    return { c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs }
