from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict
from app.core.security import get_current_user
from app.services.hr.hr_service import (
    generate_hr_set,
    submit_hr_answers
)

# ---------------------------------------------------------
# HR Interview Router
# ---------------------------------------------------------
# Handles:
# - HR question generation
# - Behavioral interview simulation
# - Answer submission & evaluation
# ---------------------------------------------------------

router = APIRouter(tags=["HR"])


# ---------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------

class HRQuestionRequest(BaseModel):
    """
    Request model for generating HR interview questions.
    """
    role: str
    company: str


class HRAnswerRequest(BaseModel):
    """
    Request model for submitting HR interview answers.
    """
    hr_set_id: str
    answers: Dict[str, str]


# ---------------------------------------------------------
# Generate HR Questions
# ---------------------------------------------------------
@router.post(
    "/questions",
    summary="Generate HR Interview Questions",
    description="""
Generates personalized HR (behavioral) interview questions.

Questions are created using:
- User resume data
- Target job role
- Target company context

Returns:
- hr_set_id → Interview session identifier
- questions → Generated HR questions
"""
)
async def get_hr_questions(
    payload: HRQuestionRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Generate HR interview questions for a specific role and company.
    """

    hr_set_id, questions = await generate_hr_set(
        user_id,
        payload.role,
        payload.company
    )

    return {
        "hr_set_id": hr_set_id,
        "questions": questions
    }


# ---------------------------------------------------------
# Submit HR Answers
# ---------------------------------------------------------
@router.post(
    "/answers",
    summary="Submit HR Interview Answers",
    description="""
Submits user's HR interview answers for evaluation.

Behavior:
- Evaluates communication quality
- Provides feedback and motivation
- Calculates overall performance score
- Stores evaluation results
"""
)
async def submit_hr_answers_route(
    payload: HRAnswerRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Submit HR interview answers and receive evaluation feedback.
    """

    return await submit_hr_answers(
        user_id,
        payload.hr_set_id,
        payload.answers
    )