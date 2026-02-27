from fastapi import APIRouter, UploadFile, File, Depends
from app.core.security import get_current_user
from app.services.resume_service import handle_resume_upload

router = APIRouter()

@router.post("/")
async def upload_resume(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    resume_id, file_url = await handle_resume_upload(file, user_id)

    return {
        "resume_id": resume_id,
        "file_url": file_url
    }