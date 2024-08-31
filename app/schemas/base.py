from datetime import datetime

from pydantic import BaseModel


class InfoBaseModel(BaseModel):
    idx: int
    created_at: datetime
    updated_at: datetime
