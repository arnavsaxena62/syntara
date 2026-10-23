from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.clerk.config import API_ALLOWED_ORIGINS
from src.db import Base, engine, ensureClerkColumn
from src.login import loginRoute
from src.llm import llmRoute

import logging
import os

logger = logging.getLogger(__name__)

logger.warning(
    "CLERK_FRONTEND_API_URL from Render: %r",
    os.getenv("CLERK_FRONTEND_API"),
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensureClerkColumn()
    yield


app = FastAPI(
    title="Syntara",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=API_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(loginRoute)
app.include_router(llmRoute)
