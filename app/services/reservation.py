from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from app.models.reservation import ReservationInfo, ReservationState
from app.schemas.user import UserInfo, UserType


class ReservationService:
    @staticmethod
    def get_reservations(
        db: Session,
        user_idx: int,
        user_type: str,
        date: Optional[datetime] = None,
        size: Optional[int] = None,
        page: Optional[int] = None
    ):
        reservations = db.query(ReservationInfo)

        if user_type != UserType.admin:
            reservations = reservations.filter(ReservationInfo.user_idx == user_idx)

        if date:
            target_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            reservations = reservations.filter(
                ReservationInfo.start_time >= target_date,
                ReservationInfo.end_time < target_date + timedelta(days=1)
            )

        if size and page:
            reservations = reservations.limit(size)
            reservations = reservations.offset(size * (page - 1))

        return reservations.all()

    @staticmethod
    def get_available_reservation_times(
        db: Session,
        start_time: datetime,
        end_time: datetime,
        applicant_count: Optional[int] = None,
        reservation_idx: Optional[int] = None
    ):
        start_hour = start_time.replace(minute=0, second=0, microsecond=0)
        end_hour = end_time.replace(minute=0, second=0, microsecond=0)

        if end_hour != end_time:
            end_hour += timedelta(hours=1)

        available_times = []

        current_time = start_hour
        not_available_times = []

        max_applicant_count = 50000
        reservation_count_limit = max_applicant_count - (applicant_count or 0)

        while current_time < end_hour:
            next_time = current_time + timedelta(hours=1)

            reservations = db.query(ReservationInfo.applicant_count).filter(
                ReservationInfo.start_time <= current_time,
                ReservationInfo.end_time >= next_time,
                ReservationInfo.state == ReservationState.confirmed,
                ReservationInfo.idx != reservation_idx if reservation_idx else True
            ).all()

            reservation_count = sum([reservation.applicant_count for reservation in reservations])
            available_count = max_applicant_count - reservation_count
            current_time_str = current_time.strftime("%H:%M")

            if reservation_count <= reservation_count_limit:
                available_times.append(
                    {
                        "time": current_time_str,
                        "available_count": available_count
                    }
                )
            else:
                not_available_times.append(
                    {
                        "time": current_time_str,
                        "available_count": available_count
                    }
                )

            current_time = next_time

        return dict(
            available_times=available_times,
            not_available_times=not_available_times,
        )

    @staticmethod
    def check_user_reservation_overlap(
        db: Session,
        user_idx: int,
        start_time: datetime,
        end_time: datetime,
        reservation_idx: Optional[int] = None
    ):
        return db.query(ReservationInfo).filter(
            ReservationInfo.user_idx == user_idx,
            ReservationInfo.state == ReservationState.confirmed,
            or_(
                and_(
                    ReservationInfo.start_time < end_time,
                    ReservationInfo.end_time > start_time
                ),
                and_(
                    ReservationInfo.start_time >= start_time,
                    ReservationInfo.start_time < end_time
                ),
                and_(
                    ReservationInfo.end_time > start_time,
                    ReservationInfo.end_time <= end_time
                )
            ),
            ReservationInfo.idx != reservation_idx if reservation_idx else True
        ).first()

    @staticmethod
    def get_exist_reservation(
        db: Session,
        user_idx: int,
        target_date: datetime
    ):
        target_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)

        return db.query(ReservationInfo).filter(
            ReservationInfo.user_idx == user_idx,
            ReservationInfo.start_time >= target_date,
            ReservationInfo.end_time < target_date + timedelta(days=1),
            ReservationInfo.state == ReservationState.confirmed
        ).all()

    @staticmethod
    def format_time_range(time_str):
        start_time = datetime.strptime(time_str, "%H:%M")
        end_time = start_time + timedelta(hours=1)
        return f"{start_time.strftime('%H:%M')} ~ {end_time.strftime('%H:%M')}"

    @classmethod
    def get_available_reservation_times_for_date(
        cls,
        db: Session,
        user_idx: int,
        user_type: UserType,
        target_date: datetime
    ):
        start_time = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)

        available_reservation_times = cls.get_available_reservation_times(db, start_time, end_time).get("available_times")
        exist_reservation = cls.get_exist_reservation(db, user_idx, target_date) if user_type == UserType.user else []

        if not available_reservation_times:
            return []

        for reservation in exist_reservation:
            start_hour = reservation.start_time.replace(minute=0, second=0, microsecond=0).time()
            end_hour = reservation.end_time.replace(minute=0, second=0, microsecond=0).time()

            overlapping_times = [
                reservation_time for reservation_time in available_reservation_times
                if start_hour <= datetime.strptime(reservation_time["time"], "%H:%M").time() < end_hour
            ]

            available_reservation_times = [
                reservation_time for reservation_time in available_reservation_times
                if reservation_time not in overlapping_times
            ]

        return [
            {
                "time": cls.format_time_range(reservation_time["time"]),
                "available_count": reservation_time["available_count"]
            }
            for reservation_time in available_reservation_times
        ]

    @classmethod
    def validate_reservation(
        cls,
        db: Session,
        user_idx: int,
        start_time: datetime,
        end_time: datetime,
        applicant_count: int,
        reservation_idx: Optional[int] = None
    ):
        if cls.check_user_reservation_overlap(db, user_idx, start_time, end_time, reservation_idx):
            raise ValueError("일정이 겹치는 예약 정보가 존재합니다.")

        result = cls.get_available_reservation_times(db, start_time, end_time, applicant_count, reservation_idx)

        available_times = result.get("available_times")
        not_available_times = result.get("not_available_times")

        if not_available_times:
            available_times = "\n".join(
                [f"{time['time']} {time['available_count']}명" for time in available_times + not_available_times if time["available_count"] > 0]
            )
            detail = "신청 가능한 인원을 초과했습니다." + (f"\n신청 가능 시간대\n{available_times}" if available_times else "")

            raise ValueError(detail)

    @classmethod
    def insert_reservation(
        cls,
        db: Session,
        user_info: UserInfo,
        start_time: datetime,
        end_time: datetime,
        applicant_count: int
    ):
        cls.validate_reservation(
            db=db,
            user_idx=user_info.idx,
            start_time=start_time,
            end_time=end_time,
            applicant_count=applicant_count,
        )

        new_reservation = ReservationInfo(
            user_idx=user_info.idx,
            start_time=start_time,
            end_time=end_time,
            applicant_count=applicant_count,
            state=ReservationState.pending,
        )

        db.add(new_reservation)
        db.commit()
        db.refresh(new_reservation)

        return new_reservation

    @classmethod
    def update_reservation(
        cls,
        db: Session,
        reservation_idx: int,
        user_type: str,
        user_idx: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        applicant_count: Optional[int] = None,
        state: Optional[ReservationState] = None
    ):
        reservation_info = db.query(ReservationInfo).filter(ReservationInfo.idx == reservation_idx).first()

        if not reservation_info:
            raise ValueError("예약 정보가 존재하지 않습니다.")

        if user_type == UserType.user and (not user_idx or reservation_info.user_idx != user_idx):
            raise ValueError("유효하지 않은 예약 정보입니다.")

        if reservation_info.state == ReservationState.canceled:
            raise ValueError("삭제된 예약 정보입니다.")

        if reservation_info.state == ReservationState.confirmed and user_type != UserType.admin:
            raise ValueError("확정된 예약 정보는 관리자만 수정할 수 있습니다.")

        if start_time:
            reservation_info.start_time = start_time

        if end_time:
            reservation_info.end_time = end_time

        if applicant_count:
            reservation_info.applicant_count = applicant_count

        cls.validate_reservation(
            db=db,
            user_idx=reservation_info.user_idx,
            start_time=reservation_info.start_time,
            end_time=reservation_info.end_time,
            applicant_count=reservation_info.applicant_count,
            reservation_idx=reservation_info.idx
        )

        if state and (user_type == UserType.admin or state == ReservationState.canceled):
            reservation_info.state = state

        db.commit()
        db.refresh(reservation_info)

        return reservation_info

    @classmethod
    def confirm_reservation(
        cls,
        db: Session,
        reservation_idx_list: List[int],
        user_type: str
    ):
        if user_type != UserType.admin:
            raise ValueError("관리자만 이용 가능한 기능입니다.")

        value_error_list = []

        for reservation_idx in reservation_idx_list:
            try:
                cls.update_reservation(
                    db=db,
                    reservation_idx=reservation_idx,
                    user_type=UserType.admin,
                    state=ReservationState.confirmed
                )
            except ValueError as e:
                value_error_list.append(
                    dict(
                        idx=reservation_idx,
                        detail=str(e)
                    )
                )

        db.commit()

        return value_error_list
