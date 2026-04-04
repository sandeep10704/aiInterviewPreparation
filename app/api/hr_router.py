from fastapi import APIRouter, Depends, WebSocket
from pydantic import BaseModel
from typing import Dict
from app.core.firebase import verify_token
from app.services.hr.hr_service_realtime import update_hr_answer_and_evaluate
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


@router.websocket("/ws")
async def hr_ws(websocket: WebSocket):

    print("HR WS STEP 1: HIT")

    # ✅ Get token (same as technical)
    token = websocket.query_params.get("token")

    if not token:
        auth_header = websocket.headers.get("authorization")
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
            except:
                pass

    if not token:
        await websocket.close(code=1008)
        return

    # ✅ Verify user
    try:
        decoded = verify_token(token)
        user_id = decoded["uid"]
        print("HR WS USER:", user_id)
    except Exception as e:
        print("HR WS TOKEN ERROR:", e)
        await websocket.close(code=1008)
        return

    # ✅ Accept connection
    await websocket.accept()
    print("HR WS CONNECTED")

    try:
        while True:
            data = await websocket.receive_text()
            print("HR WS RECEIVED:", data)

            try:
                parsed = json.loads(data)
            except:
                await websocket.send_json({"error": "Invalid JSON"})
                continue

            # ✅ Expected input:
            # {
            #   "hr_set_id": "...",
            #   "question_no": 1,
            #   "answer": "..."
            # }

            try:
                result = await update_hr_answer_and_evaluate(
                    user_id,
                    parsed.get("hr_set_id"),
                    parsed.get("question_no"),
                    parsed.get("answer")
                )

                await websocket.send_json(result)

            except Exception as e:
                print("HR WS ERROR:", e)
                await websocket.send_json({"error": "Processing failed"})

    except Exception as e:
        print("HR WS CLOSED:", e)