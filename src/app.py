import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import ALLOWED_ORIGINS
from .database.create_table import (
    create_database,
    create_tables,
)
from .routes import chat, health, ingestion, metrics
from .vectorstore.create_index import (
    ensure_collection,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize required services for the application lifespan."""

    try:
        create_database()
        create_tables()
    except Exception:
        logger.exception("Postgres startup initialization failed")

    try:
        ensure_collection()
    except Exception:
        logger.exception("Astra DB collection initialization failed")

    yield


app = FastAPI(title="AI Investor Intelligence Platform API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(metrics.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(ingestion.router, prefix="/api")
