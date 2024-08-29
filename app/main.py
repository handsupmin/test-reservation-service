from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import engine
from app.db.init_db import init_db

def startup():
    init_db(engine)

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

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI!"}
