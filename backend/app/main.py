"""Application entrypoint."""

import logging

from fastapi import FastAPI

from app.database.engine import create_tables
from app.notes.api.v1.router import router as router_notes

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app = FastAPI(
    title="Notes App",
    description="Apple Notes clone with DDD + Hexagonal Architecture",
    version="0.1.0",
)

# Development: create tables from ORM metadata at startup.
# Production: use Alembic migrations instead.
create_tables()

app.include_router(router_notes)
