from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class FeedbackRequest(BaseModel):
    session_id: str  # technical_set_id or coding_set_id


@router.get("/{session_id}")
def get_feedback(session_id: str):
    """
    Get feedback for a session
    """
    return {
        "session_id": session_id,
        "score": 8.5,
        "feedback": "Strong understanding but improve edge case handling."
    }