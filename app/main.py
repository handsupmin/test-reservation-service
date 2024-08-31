from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import reservation, base
from app.db.init_db import init_db


def startup():
    init_db()


def shutdown():
    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    startup()

    yield

    shutdown()


app = FastAPI(lifespan=lifespan)

# middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# router
app.include_router(base.router, prefix="", tags=["base"])
app.include_router(reservation.router, prefix="/api", tags=["reservations"])
