from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.token import TokenInfo
from app.schemas.user import UserInfo


def get_user_from_token(db: Session, token: str) -> UserInfo:
    token_info = db.query(TokenInfo).filter(TokenInfo.token == token).first()

    if not token_info or token_info.expired_at < datetime.now():
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

    return UserInfo(idx=token_info.user_idx, type=token_info.user_type.value)


def refresh_token(db: Session):
    now = datetime.now()
    expired_at = now + timedelta(days=1)

    tokens = db.query(TokenInfo).all()

    if tokens:
        db.query(TokenInfo).update({ TokenInfo.expired_at: expired_at }, synchronize_session=False)
    else:
        insert_data = [
            TokenInfo(user_idx=1, user_type="admin", token="admin1", expired_at=expired_at),
            TokenInfo(user_idx=2, user_type="admin", token="admin2", expired_at=expired_at),
            TokenInfo(user_idx=3, user_type="admin", token="admin3", expired_at=expired_at),
            TokenInfo(user_idx=1, user_type="user", token="user1", expired_at=expired_at),
            TokenInfo(user_idx=2, user_type="user", token="user2", expired_at=expired_at),
            TokenInfo(user_idx=3, user_type="user", token="user3", expired_at=expired_at),
            TokenInfo(user_idx=4, user_type="user", token="user4", expired_at=expired_at),
            TokenInfo(user_idx=5, user_type="user", token="user5", expired_at=expired_at),
        ]
        db.add_all(insert_data)

    db.commit()
