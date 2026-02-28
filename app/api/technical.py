from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.services.technical.technical_service import (
    generate_technical_set,
    get_or_create_user_technical_set,
    submit_answers,
    get_master_technical_sets,
)
from app.schemas.technical.technical_request_schema import TechnicalAnswerRequest

# ---------------------------------------------------------
# Technical Interview Router
# ---------------------------------------------------------
# Handles:
# - Technical question generation
# - Interview session retrieval
# - Answer submission & evaluation
# - Technical interview history
# ---------------------------------------------------------

router = APIRouter(tags=["Technical"])


# ---------------------------------------------------------
# Generate Technical Questions
# ---------------------------------------------------------
@router.get(
    "/questions",
    summary="Generate Technical Interview Questions",
    description="""
Generates a personalized technical interview question set.

Questions are created using:
- User resume data
- Skills and projects
- AI research context

Returns:
- technical_set_id → Interview session identifier
- questions → Generated technical Q&A
"""
)
async def get_technical_questions(
    user_id: str = Depends(get_current_user)
):
    """
    Generate a new technical interview session.
    """
    technical_set_id, questions = await generate_technical_set(user_id)

    return {
        "technical_set_id": technical_set_id,
        "questions": questions
    }


# ---------------------------------------------------------
# Submit Technical Answers
# ---------------------------------------------------------
@router.post(
    "/answers",
    summary="Submit Technical Interview Answers",
    description="""
Submits user answers for technical interview evaluation.

Behavior:
- Evaluates correctness and explanation quality
- Generates technical feedback
- Calculates overall score
- Stores evaluation results
"""
)
async def submit_technical_answers(
    payload: TechnicalAnswerRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Submit answers for a technical interview session.
    """
    return await submit_answers(
        user_id,
        payload.technical_set_id,
        payload.answers
    )


# ---------------------------------------------------------
# List Technical Interview Sets
# ---------------------------------------------------------
@router.get(
    "/sets",
    summary="List Technical Interview Sessions",
    description="""
Returns all technical interview sessions available for the user.

Used for:
- Interview history dashboard
- Resume previous sessions
"""
)
async def list_master_sets(
    user_id: str = Depends(get_current_user)
):
    """
    Retrieve all technical interview set IDs for the user.
    """
    return await get_master_technical_sets(user_id)


# ---------------------------------------------------------
# Open Technical Interview Session
# ---------------------------------------------------------
@router.get(
    "/sets/{technical_set_id}",
    summary="Open Technical Interview Session",
    description="""
Retrieves a specific technical interview session.

Behavior:
- Fetches questions from master collection
- Creates user session copy if not already created
- Allows interview resumption
"""
)
async def get_master_set(
    technical_set_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Load or initialize a technical interview session.
    """
    return await get_or_create_user_technical_set(
        user_id,
        technical_set_id
    )