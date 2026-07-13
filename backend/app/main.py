from fastapi import FastAPI

app = FastAPI()


@app.post("/api/v1/notes")
def create_note():
    return {"status": "success"}
