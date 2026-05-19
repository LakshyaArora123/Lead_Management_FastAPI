from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app=FastAPI(
    title="Lead Management API",
    description="A simple REST API for managing sales leads.",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/health", tags=["Health"], summary="Health check")
async def health():
    return {"status": "ok"}
