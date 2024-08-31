from datetime import datetime
from enum import Enum
from functools import wraps

from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.db.base import Base, to_dict


def convert_for_json(obj):
    if isinstance(obj, Base):
        return convert_for_json(to_dict(obj))

    if isinstance(obj, BaseModel):
        return convert_for_json(obj.model_dump())

    if isinstance(obj, datetime):
        return str(obj)

    if isinstance(obj, Enum):
        return obj.value

    if isinstance(obj, dict):
        return { key: convert_for_json(value) for key, value in obj.items() }

    if isinstance(obj, list):
        return [convert_for_json(item) for item in obj]

    return obj


def json_result_wrapper(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        return JSONResponse(content={ "result": convert_for_json(result) })

    return wrapper
