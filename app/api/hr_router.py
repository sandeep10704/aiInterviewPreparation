from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict
from app.core.security import get_current_user
from app.services.hr_service import (
    generate_hr_set,
    submit_hr_answers
)

router = APIRouter()

class HRQuestionRequest(BaseModel):
    role: str
    company: str


class HRAnswerRequest(BaseModel):
    hr_set_id: str
    answers: Dict[str, str]

@router.post("/questions")
async def get_hr_questions(
    payload: HRQuestionRequest,
    user_id: str = Depends(get_current_user)
):

    hr_set_id, questions = await generate_hr_set(
        user_id,
        payload.role,
        payload.company
    )

    return {
        "hr_set_id": hr_set_id,
        "questions": questions
    }

@router.post("/answers")
async def submit_hr_answers_route(
    payload: HRAnswerRequest,
    user_id: str = Depends(get_current_user)
):
    return await submit_hr_answers(
        user_id,
        payload.hr_set_id,
        payload.answers
    )