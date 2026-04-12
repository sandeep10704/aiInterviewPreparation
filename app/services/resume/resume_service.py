import uuid
import time
from datetime import datetime
from app.core.supabase_client import supabase
from app.services.user_service import update_user_resume_full
from app.services.resume.resume_parser_service import extract_text_from_url, parse_resume


def upload_with_retry(bucket, path, file_bytes, content_type):
    for attempt in range(5):
        try:
            print(f"Uploading to Supabase... attempt {attempt+1}")
            return supabase.storage.from_(bucket).upload(
                path=path,
                file=file_bytes,
                file_options={"content-type": content_type}
            )
        except Exception as e:
            print("Supabase sleeping... retrying", e)
            time.sleep(3)

    raise Exception("Supabase still sleeping after retries")


async def handle_resume_upload(file, user_id: str):
    resume_id = str(uuid.uuid4())
    file_bytes = await file.read()
    file_path = f"{resume_id}_{file.filename}"

    # Upload to Supabase (with retry)
    upload_with_retry(
        "resume",
        file_path,
        file_bytes,
        file.content_type
    )

    # Create signed URL
    signed = supabase.storage.from_("resume").create_signed_url(
        file_path,
        3600
    )

    file_url = signed["signedURL"]

    # -------- PARALLEL SAFE SECTION --------
    text = extract_text_from_url(file_url)
    structured_data = parse_resume(text)

    # Update user document
    update_user_resume_full(
        user_id=user_id,
        resume_id=resume_id,
        resume_data=structured_data
    )

    return resume_id, file_url