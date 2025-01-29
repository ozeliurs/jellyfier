from fastapi import FastAPI

from src.database import create_db_and_tables
from src.routers import file_router

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(file_router, prefix="/files", tags=["files"])


@app.get("/")
def read_root():
    return {"Hello": "World"}
