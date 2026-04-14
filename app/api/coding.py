from fastapi import APIRouter, Depends, WebSocket

from app.core.security import get_current_user, verify_token

from app.schemas.coding.QuestionRequest import QuestionRequest
from app.schemas.coding.coding_submit_schema import CodingSubmitRequest
from app.schemas.coding.coding_run_schema import CodingRunRequest
from app.schemas.coding.coding_playground_schema import CodingPlaygroundRequest

from app.services.coding.coding_service import (
    generate_coding_set,
    submit_coding_solution,
    get_coding_sets,
    get_coding_set_questions
)
from app.core.security import get_current_user_ws
from app.services.coding.coding_runner_service import run_user_code_preview
from app.services.coding.coding_playground_service import run_playground_code
from app.services.coding.coding_ws_service import coding_ws_handler
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
@router.post(
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
    payload: QuestionRequest,
    user_id: str = Depends(get_current_user)
):
    coding_set_id, questions = await generate_coding_set(
        user_id,
        payload.count,
        payload.level
    )

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
    payload.code,
    payload.language
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




# in your router file

@router.websocket("/ws")
async def coding_ws(websocket: WebSocket):

    print("🔥 WS HIT")   # MUST print

    token = websocket.query_params.get("token")
    print("🔑 TOKEN:", token[:30] if token else "None")

    if not token:
        print("❌ NO TOKEN")
        await websocket.close(code=1008)
        return

    try:
        from app.core.security import get_current_user_ws
        user_id = await get_current_user_ws(token)
        print("✅ AUTH SUCCESS:", user_id)
    except Exception as e:
        print("❌ WS AUTH ERROR:", e)
        await websocket.close(code=1008)
        return

    await websocket.accept()
    print("🟢 WS CONNECTED")

    await coding_ws_handler(websocket, user_id)

@router.get(
    "/sets",
    summary="Get Coding Sets",
    description="Returns all coding interview set IDs for user"
)
async def get_sets(
    user_id: str = Depends(get_current_user)
):
    return await get_coding_sets(user_id)

@router.get(
    "/sets/{coding_set_id}",
    summary="Get Coding Set Questions",
    description="""
Returns:
- questions
- first 3 test cases
"""
)
async def get_set_questions(
    coding_set_id: str,
    user_id: str = Depends(get_current_user)
):
    return await get_coding_set_questions(
        user_id,
        coding_set_id
    )
