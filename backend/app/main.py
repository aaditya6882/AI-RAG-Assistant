from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.documents import router as documents_router
from app.api.chat import router as chat_router
from app.database import test_database_connection


FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

app = FastAPI(
    title="AI RAG Assistant",
    description="Retrieval-Augmented Generation API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router)
app.include_router(chat_router)


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.get("/health/database")
def database_health():
    try:
        connected = test_database_connection()

        return {
            "database": "connected" if connected else "not connected"
        }

    except Exception as error:
        return {
            "database": "error",
            "detail": str(error),
        }


@app.get("/")
def root():
    index = FRONTEND_DIR / "index.html"
    if not index.exists():
        return {
            "message": "AI RAG Assistant API",
            "status": "running",
        }
    return FileResponse(index)


if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
