from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database import create_db_and_tables
from src.routers import file_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(file_router, prefix="/files", tags=["files"])


@app.get("/")
def read_root():
    return {"Hello": "World"}
