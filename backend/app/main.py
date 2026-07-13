import logging

from fastapi import FastAPI

logger = logging.getLogger(__name__)

app = FastAPI()


@app.post("/api/v1/notes")
def create_note():
    logger.info("POST /api/v1/notes")
    return {"status": "success"}
