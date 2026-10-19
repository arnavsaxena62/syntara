from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.db import Base, engine
from src.login import loginRoute
from src.llm import llmRoute

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Authentication Demo",
    version="1.0.0",
    lifespan=lifespan,
)

origins = [
    "http://192.168.1.17:3001",
    "http://localhost:3000",
    "http://localhost:3001",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(loginRoute)
app.include_router(llmRoute)