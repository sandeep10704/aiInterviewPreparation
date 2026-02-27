from app.core.firebase import db
from datetime import datetime

def update_user_resume_id(user_id: str, resume_id: str):
    """
    Updates only resume_id field.
    Other fields remain untouched.
    """

    user_ref = db.collection("users").document(user_id)

    user_ref.set(
        {
            "resume_id": resume_id,
            "updated_at": datetime.utcnow()
        },
        merge=True  # Important: prevents overwriting entire document
    )
def update_user_resume_full(user_id: str, resume_id: str, resume_data: dict):
    user_ref = db.collection("users").document(user_id)

    user_ref.set(
        {
            "resume_id": resume_id,
            "resume_data": resume_data,
            "updated_at": datetime.utcnow()
        },
        merge=True
    )