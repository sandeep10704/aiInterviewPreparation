from fastapi import APIRouter, UploadFile, File, Depends
from app.core.security import get_current_user
from app.services.resume_service import handle_resume_upload

# ---------------------------------------------------------
# Resume Management Router
# ---------------------------------------------------------
# Handles:
# - Resume upload
# - Resume storage
# - Resume parsing trigger
# ---------------------------------------------------------

router = APIRouter(tags=["Resume"])


# ---------------------------------------------------------
# Upload Resume
# ---------------------------------------------------------
@router.post(
    "/",
    summary="Upload Resume",
    description="""
Uploads a user's resume file.

Behavior:
- Accepts resume file (PDF/DOC/DOCX)
- Stores file in cloud storage
- Associates resume with authenticated user
- Triggers resume processing pipeline

Returns:
- resume_id → Unique identifier for uploaded resume
- file_url → Accessible storage URL
"""
)
async def upload_resume(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    """
    Upload a resume for the authenticated user.

    Parameters:
    - file: Resume document uploaded as multipart/form-data
    - user_id: Retrieved automatically from authentication token

    Returns:
    - resume_id (str)
    - file_url (str)
    """

    resume_id, file_url = await handle_resume_upload(file, user_id)

    return {
        "resume_id": resume_id,
        "file_url": file_url
    }