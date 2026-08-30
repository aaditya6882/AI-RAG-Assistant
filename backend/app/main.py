from fastapi import FastAPI

from app.api.documents import router as documents_router
from app.database import test_database_connection


app = FastAPI(
    title="AI RAG Assistant",
    description="Retrieval-Augmented Generation API",
    version="1.0.0",
)


app.include_router(documents_router)


@app.get("/")
def root():
    return {
        "message": "AI RAG Assistant API",
        "status": "running",
    }


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
            "database": "connected"
            if connected
            else "not connected"
        }

    except Exception as error:
        return {
            "database": "error",
            "detail": str(error),
        }