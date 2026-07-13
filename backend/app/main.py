import logging

from fastapi import FastAPI

from app.notes.api.v1.router import router as router_notes

# logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI()

app = FastAPI(
    title="Notes App",
    description="Apple Notes clone with DDD + Hexagonal Architecture",
    version="0.1.0",
)


# @app.post("/api/v1/notes")
# def create_note():
#     logger.info("POST /api/v1/notes")
#     return {"status": "success"}

app.include_router(router_notes)
