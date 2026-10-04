from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.rag_service import answer_question


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    question: str
    limit: int = 5


@router.post("/")
def chat(request: ChatRequest):

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        return answer_question(
            request.question,
            limit=request.limit,
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )