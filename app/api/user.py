from fastapi import APIRouter
from app.core.firebase import db
from datetime import datetime
from app.schemas.user import UserCreate
router = APIRouter()

@router.post("/")
async def create_user_profile(user_id: str, user: UserCreate):

    user_data = user.dict()
    user_data["created_at"] = datetime.utcnow()

    db.collection("users").document(user_id).set(user_data)

    return {"message": "User profile created successfully"}