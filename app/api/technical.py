from app.services.technical.realtime_service import update_answer_and_evaluate
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.services.technical.technical_service import (
    generate_technical_set,
    get_or_create_user_technical_set,
    submit_answers,
    get_master_technical_sets,
)
from app.schemas.technical.technical_request_schema import TechnicalAnswerRequest
import json
from fastapi import WebSocket
from app.core.firebase import verify_token
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


# @router.websocket("/ws")
# async def technical_ws(websocket: WebSocket):
#     await websocket.accept()
#     print("WebSocket connected")



@router.websocket("/ws")
async def technical_ws(websocket: WebSocket):

    print("STEP 1: WS HIT")
    print("HEADERS:", websocket.headers)
    print("QUERY:", websocket.query_params)

    # ✅ Try query param first (Postman / frontend)
    token = websocket.query_params.get("token")
    print("STEP 2: TOKEN FROM QUERY:", token)

    # ✅ Fallback to Authorization header
    if not token:
        auth_header = websocket.headers.get("authorization")
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
                print("STEP 3: TOKEN FROM HEADER:", token)
            except:
                print("STEP 3: INVALID AUTH HEADER FORMAT")

    # ❌ No token → close
    if not token:
        print("STEP 4: NO TOKEN FOUND")
        await websocket.close(code=1008)
        return

    # ✅ Verify token
    try:
        decoded = verify_token(token)
        user_id = decoded["uid"]
        print("STEP 5: USER ID:", user_id)
    except Exception as e:
        print("STEP 5: TOKEN ERROR:", e)
        await websocket.close(code=1008)
        return

    # ✅ Accept connection
    await websocket.accept()
    print("STEP 6: CONNECTION ACCEPTED")

    try:
        while True:
            print("STEP 7: WAITING FOR MESSAGE...")

            data = await websocket.receive_text()
            print("STEP 8: RECEIVED RAW:", data)

            try:
                parsed = json.loads(data)
                print("STEP 9: PARSED:", parsed)
            except Exception as e:
                print("STEP 9: JSON ERROR:", e)
                await websocket.send_json({"error": "Invalid JSON"})
                continue

            # ✅ Process logic
            try:
                result = await update_answer_and_evaluate(
                    user_id,
                    parsed.get("technical_set_id"),
                    parsed.get("question_no"),
                    parsed.get("answer")
                )

                print("STEP 10: RESULT:", result)
                await websocket.send_json(result)

            except Exception as e:
                print("STEP 10: PROCESS ERROR:", e)
                await websocket.send_json({"error": "Processing failed"})

    except Exception as e:
        print("STEP FINAL ERROR:", e)
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