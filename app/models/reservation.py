import enum

from sqlalchemy import Column, Integer, Enum, DateTime, Index

from app.db.base import Base


class ReservationState(enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    canceled = "canceled"


class ReservationInfo(Base):
    __tablename__ = "reservation_info"

    user_idx = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    applicant_count = Column(Integer, nullable=False)
    state = Column(Enum(ReservationState), nullable=False)

    __table_args__ = (
        Index("idx_reservation_time", "start_time", "end_time", postgresql_using="brin"),
    )
