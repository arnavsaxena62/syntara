from fastapi import FastAPI
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

app.include_router(loginRoute)
app.include_router(llmRoute)