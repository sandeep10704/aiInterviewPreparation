from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.services.technical_service import (
    generate_technical_set,
    submit_answers
)
from app.models.technical_request_schema import TechnicalAnswerRequest
router = APIRouter()


@router.get("/questions")
async def get_technical_questions(
    user_id: str = Depends(get_current_user)
):
    technical_set_id, questions = await generate_technical_set(user_id)

    return {
        "technical_set_id": technical_set_id,
        "questions": questions
    }


@router.post("/answers")
async def submit_technical_answers(
    payload: TechnicalAnswerRequest,
    user_id: str = Depends(get_current_user)
):
    return await submit_answers(
        user_id,
        payload.technical_set_id,
        payload.answers
    )