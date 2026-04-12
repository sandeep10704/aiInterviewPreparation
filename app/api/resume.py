from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.core.security import get_current_user
from app.services.resume.resume_service import handle_resume_upload

router = APIRouter(tags=["Resume"])


@router.post(
    "/",
    summary="Upload Resume",
)
async def upload_resume(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    try:
        # DEBUG logs
        print("=========== RESUME UPLOAD ===========")
        print("Filename:", file.filename)
        print("Content type:", file.content_type)
        print("User ID:", user_id)

        resume_id, file_url = await handle_resume_upload(file, user_id)

        print("UPLOAD SUCCESS:", resume_id)

        return {
            "resume_id": resume_id,
            "file_url": file_url
        }

    except Exception as e:
        print("UPLOAD FAILED:", str(e))
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )