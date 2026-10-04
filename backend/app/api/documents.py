from pathlib import Path
import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.rag.vector_store import list_documents
from app.services.document_service import process_pdf


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
)


@router.get("/")
def get_documents():
    try:
        return {"documents": list_documents()}
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_document(
    document: UploadFile = File(...)
):
    if not document.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided.",
        )

    if not document.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    document_path = UPLOAD_DIR / document.filename

    try:
        with document_path.open("wb") as buffer:
            shutil.copyfileobj(document.file, buffer)

        result = process_pdf(str(document_path))

        return {
            "message": "PDF processed successfully.",
            **result,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    finally:
        document.file.close()