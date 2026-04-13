from fastapi import APIRouter, Depends
from datetime import datetime
from app.core.firebase import db
from app.core.security import get_current_user

router = APIRouter(tags=["User"])


# ---------------- GET USER ----------------
@router.get("/")
async def get_user_profile(
    user_id: str = Depends(get_current_user)
):

    doc = db.collection("users").document(user_id).get()

    if not doc.exists:
        return {}

    data = doc.to_dict()
    resume = data.get("resume_data", {})

    response = {

        # ---------- RESUME ----------
        "name": resume.get("name"),
        "email": resume.get("email"),
        "phone": resume.get("phone"),
        "skills": resume.get("skills"),
        "projects": resume.get("projects"),
        "education": resume.get("education"),
        "work_experience": resume.get("work_experience"),
        "certifications": resume.get("certifications"),
        "achievements": resume.get("achievements"),

        # ---------- USER FIELDS ----------
        "target_role": data.get("target_role"),
        "experience_level": data.get("experience_level"),
        "preferred_locations": data.get("preferred_locations"),

        # ---------- INTERVIEWS ----------
        "upcoming_interviews": data.get("upcoming_interviews"),
        "applied_companies": data.get("applied_companies"),
        "selected_companies": data.get("selected_companies"),
        "rejected_companies": data.get("rejected_companies"),

        # ---------- PROGRESS ----------
        "coding_progress": data.get("coding_progress"),
        "technical_progress": data.get("technical_progress"),
        "hr_progress": data.get("hr_progress"),

        # ---------- PROFILE ----------
        "strengths": data.get("strengths"),
        "weaknesses": data.get("weaknesses"),
        "career_goal": data.get("career_goal"),

        # ---------- META ----------
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at")
    }

    return response


# ---------------- UPDATE USER ----------------
@router.put("/")
async def update_user_profile(
    payload: dict,
    user_id: str = Depends(get_current_user)
):

    payload["updated_at"] = datetime.utcnow()

    db.collection("users").document(user_id).set(
        payload,
        merge=True
    )

    return {"message": "User updated"}