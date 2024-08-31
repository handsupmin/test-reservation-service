from app.db.base import engine, Base
from app.db.session import SessionLocal
from app.services.token import refresh_token


def init_db():
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        refresh_token(session)
    finally:
        session.close()
