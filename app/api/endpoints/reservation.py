from datetime import datetime, timedelta
from typing import List, Dict, Union, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.decorator import json_result_wrapper
from app.db.session import get_db
from app.dependencies.auth import get_token
from app.models.reservation import ReservationState
from app.schemas.reservation import Reservation, ReservationPostRequest, ReservationGetResult, ReservationConfirmRequest, ReservationPutRequest, ReservationDeleteRequest
from app.schemas.user import UserType
from app.services.reservation import ReservationService
from app.services.token import get_user_from_token

router = APIRouter()


@router.get("/reservations/available", response_model=List[Dict[str, Union[str, int]]])
@json_result_wrapper
def get_available_reservation_times(
    date: str,
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    user_info = get_user_from_token(db, token)

    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="유효한 날짜 형식이 아닙니다. YYYY-MM-DD 형식의 날짜를 입력해주세요.")

    return ReservationService.get_available_reservation_times_for_date(db, user_info.idx, user_info.type, target_date)


@router.get("/reservations", response_model=List[ReservationGetResult])
@json_result_wrapper
def get_reservations(
    date: Optional[str] = None,
    size: Optional[int] = None,
    page: Optional[int] = None,
    db: Session = Depends(get_db),
    token: str = Depends(get_token),
):
    user_info = get_user_from_token(db, token)

    if date:
        try:
            date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="유효한 날짜 형식이 아닙니다. YYYY-MM-DD 형식의 날짜를 입력해주세요.")

    if (size and not page) or (page and not size):
        raise HTTPException(status_code=400, detail="size와 page는 함께 사용해야 합니다.")

    reservations = ReservationService.get_reservations(
        db=db,
        user_idx=user_info.idx,
        user_type=user_info.type,
        date=date,
        size=size,
        page=page
    )

    return list(
        ReservationGetResult(
            idx=reservation.idx,
            user_idx=reservation.user_idx,
            start_time=reservation.start_time,
            end_time=reservation.end_time,
            applicant_count=reservation.applicant_count,
            state=reservation.state.value,
        ) for reservation in reservations
    )


@router.post("/reservations", response_model=Reservation)
@json_result_wrapper
def insert_reservation(
    request: ReservationPostRequest,
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    user_info = get_user_from_token(db, token)

    if user_info.type != UserType.user:
        raise HTTPException(status_code=403, detail="관리자는 예약할 수 없습니다.")

    if request.start_time < datetime.now() + timedelta(days=3):
        raise HTTPException(status_code=400, detail="예약은 시험 시작 3일 전까지 신청 가능합니다.")

    try:
        new_reservation = ReservationService.insert_reservation(
            db=db,
            user_info=user_info,
            start_time=request.start_time,
            end_time=request.end_time,
            applicant_count=request.applicant_count
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return new_reservation


@router.put("/reservations/confirm", response_model=List[int])
@json_result_wrapper
def confirm_reservation(
    request: ReservationConfirmRequest,
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    user_info = get_user_from_token(db, token)

    try:
        value_error_list = ReservationService.confirm_reservation(
            db=db,
            reservation_idx_list=request.reservation_idx_list,
            user_type=user_info.type
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return value_error_list if value_error_list else { "state": "success" }


@router.put("/reservations", response_model=Reservation)
@json_result_wrapper
def update_reservation(
    request: ReservationPutRequest,
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    user_info = get_user_from_token(db, token)

    try:
        updated_reservation = ReservationService.update_reservation(
            db=db,
            reservation_idx=request.idx,
            user_idx=user_info.idx,
            user_type=user_info.type,
            start_time=request.start_time,
            end_time=request.end_time,
            applicant_count=request.applicant_count,
            state=request.state
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return updated_reservation


@router.delete("/reservations")
def delete_reservation(
    request: ReservationDeleteRequest,
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    user_info = get_user_from_token(db, token)

    try:
        ReservationService.update_reservation(
            db=db,
            reservation_idx=request.idx,
            user_idx=user_info.idx,
            user_type=user_info.type,
            state=ReservationState.canceled
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return { "state": "success" }
