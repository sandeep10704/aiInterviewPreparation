from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.services.coding_service import generate_coding_set
from app.models.coding_submit_schema import CodingSubmitRequest
from app.services.coding_service import submit_coding_solution
router = APIRouter()


@router.get("/questions")
async def get_coding_questions(
    user_id: str = Depends(get_current_user)
):

    coding_set_id, questions = await generate_coding_set(user_id)

    return {
        "coding_set_id": coding_set_id,
        "questions": questions
    }

@router.post("/submit")
async def submit_code(
    payload: CodingSubmitRequest,
    user_id: str = Depends(get_current_user)
):

    return await submit_coding_solution(
        user_id,
        payload.coding_set_id,
        payload.question_index,
        payload.code
    )