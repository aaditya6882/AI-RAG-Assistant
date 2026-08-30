from pathlib import Path
import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.document_service import process_pdf


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided.",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    file_path = UPLOAD_DIR / file.filename

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = process_pdf(str(file_path))

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
        file.file.close()