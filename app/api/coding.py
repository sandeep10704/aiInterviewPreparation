from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.services.coding.coding_service import generate_coding_set, submit_coding_solution
from app.schemas.coding.coding_submit_schema import CodingSubmitRequest
from app.schemas.coding.coding_run_schema import CodingRunRequest
from app.services.coding.coding_runner_service import run_user_code_preview
from app.schemas.coding.coding_playground_schema import CodingPlaygroundRequest
from app.services.coding.coding_playground_service import run_playground_code

# ---------------------------------------------------------
# Coding Interview Router
# ---------------------------------------------------------
# Handles:
# - Coding question generation
# - Code preview execution (Run)
# - Final solution submission
# - Coding playground execution
# ---------------------------------------------------------

router = APIRouter(tags=["Coding"])


# ---------------------------------------------------------
# Generate Coding Questions
# ---------------------------------------------------------
@router.get(
    "/questions",
    summary="Generate Coding Questions",
    description="""
Generates personalized coding interview questions based on the user's resume.

Returns:
- coding_set_id → Unique interview session ID
- questions → Generated coding problems
"""
)
async def get_coding_questions(
    user_id: str = Depends(get_current_user)
):
    """
    Generate a new coding interview set for the authenticated user.
    """
    coding_set_id, questions = await generate_coding_set(user_id)

    return {
        "coding_set_id": coding_set_id,
        "questions": questions
    }


# ---------------------------------------------------------
# Submit Coding Solution (Final Evaluation)
# ---------------------------------------------------------
@router.post(
    "/submit",
    summary="Submit Coding Solution",
    description="""
Submits user solution for evaluation.

Behavior:
- Runs code against ALL test cases
- Stores submission results
- Calculates score and evaluation
"""
)
async def submit_code(
    payload: CodingSubmitRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Submit final coding solution for evaluation.
    """
    return await submit_coding_solution(
        user_id,
        payload.coding_set_id,
        payload.question_index,
        payload.code
    )


# ---------------------------------------------------------
# Run Code Preview (First 3 Test Cases)
# ---------------------------------------------------------
@router.post(
    "/run",
    summary="Run Code (Preview)",
    description="""
Executes user code against the FIRST 3 test cases only.

Used for:
- Run button in coding editor
- Quick validation before submission

Does NOT store results in database.
"""
)
async def run_code_preview(
    payload: CodingRunRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Run preview execution of coding solution.
    """
    return await run_user_code_preview(
        user_id=user_id,
        coding_set_id=payload.coding_set_id,
        question_no=payload.question_no,
        code=payload.code,
        language=payload.language
    )


# ---------------------------------------------------------
# Coding Playground
# ---------------------------------------------------------
@router.post(
    "/playground",
    summary="Coding Playground Execution",
    description="""
Executes custom code with user-provided input.

Features:
- No question required
- No database storage
- Supports multiple programming languages
- Acts like an online coding console
"""
)
async def coding_playground(payload: CodingPlaygroundRequest):
    """
    Execute arbitrary code in playground mode.
    """
    return await run_playground_code(
        code=payload.code,
        language=payload.language,
        stdin=payload.stdin
    )