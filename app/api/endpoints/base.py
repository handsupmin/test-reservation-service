from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.token import refresh_token

router = APIRouter()


# post refresh token

@router.post("/refresh_token")
def refresh_user_token(db: Session = Depends(get_db)):
    refresh_token(db)
    return { "state": "success" }
