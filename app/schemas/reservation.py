from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, model_validator

from app.schemas.base import InfoBaseModel


class ReservationState(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    canceled = "canceled"


class Reservation(InfoBaseModel):
    idx: int
    user_idx: int
    start_time: datetime
    end_time: datetime
    applicant_count: int
    state: ReservationState
    created_at: datetime
    updated_at: datetime


class ReservationGetResult(BaseModel):
    idx: int
    user_idx: int
    start_time: datetime
    end_time: datetime
    applicant_count: int
    state: ReservationState


class ReservationBaseModel(BaseModel):
    start_time: datetime
    end_time: datetime
    applicant_count: int

    @model_validator(mode="before")
    @classmethod
    def check_start_end_time(cls, data):
        start_time = data.get("start_time", None)
        end_time = data.get("end_time", None)
        applicant_count = data.get("applicant_count", None)

        if (start_time and not end_time) or (end_time and not start_time):
            raise ValueError("시작 시간과 종료 시간은 함께 입력해야 합니다.")

        if start_time and end_time and start_time >= end_time:
            raise ValueError("시작 시간이 종료 시간보다 같거나 늦을 수 없습니다.")

        if not (0 < applicant_count <= 50000):
            raise ValueError("유효하지 않은 신청자 수입니다. 1 이상 50000 이하의 수를 입력해주세요.")

        return data


class ReservationPostRequest(ReservationBaseModel):
    pass


class ReservationConfirmRequest(BaseModel):
    reservation_idx_list: List[int]


class ReservationPutRequest(ReservationBaseModel):
    idx: int
    state: Optional[ReservationState]


class ReservationDeleteRequest(BaseModel):
    idx: int
