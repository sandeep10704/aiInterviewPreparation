import uuid
import time
from datetime import datetime

from app.core.supabase_client import supabase
from app.core.firebase import db
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


# -----------------------------
# CREATE SAMPLE CODING SET (ID=1)
# -----------------------------
def create_sample_coding_set(user_id: str):

    user_ref = db.collection("users").document(user_id)

    coding_questions = [
        {
            "difficulty": "Easy",
            "title": "Reverse String",
            "function_signature": "def reverse_string(s: str) -> str:",
            "problem_statement": "Reverse the given string.",
            "test_cases": [
                {"input": "hello", "output": "olleh"},
                {"input": "abc", "output": "cba"},
                {"input": "a", "output": "a"},
                {"input": "python", "output": "nohtyp"},
                {"input": "12345", "output": "54321"},
                {"input": "", "output": ""}
            ]
        },
        {
            "difficulty": "Easy",
            "title": "Find Maximum in Array",
            "function_signature": "def find_max(arr: list) -> int:",
            "problem_statement": "Return maximum element in array.",
            "test_cases": [
                {"input": "[1,2,3]", "output": "3"},
                {"input": "[5,1,2]", "output": "5"},
                {"input": "[10]", "output": "10"},
                {"input": "[-1,-2,-3]", "output": "-1"},
                {"input": "[7,7,7]", "output": "7"},
                {"input": "[100,50,200,10]", "output": "200"}
            ]
        }
    ]

    user_ref.collection("coding_questions") \
        .document("1") \
        .set({
            "coding_set_id": "1",
            "questions": coding_questions,
            "answers": {},
            "status": "pending",
            "created_at": datetime.utcnow()
        })


# -----------------------------
# MAIN UPLOAD FUNCTION
# -----------------------------
async def handle_resume_upload(file, user_id: str):

    resume_id = str(uuid.uuid4())
    file_bytes = await file.read()
    file_path = f"{resume_id}_{file.filename}"

    # Upload to Supabase
    upload_with_retry(
        "resume",
        file_path,
        file_bytes,
        file.content_type
    )

    # signed URL
    signed = supabase.storage.from_("resume").create_signed_url(
        file_path,
        3600
    )

    file_url = signed["signedURL"]

    # parse resume
    text = extract_text_from_url(file_url)
    structured_data = parse_resume(text)

    # update user
    update_user_resume_full(
        user_id=user_id,
        resume_id=resume_id,
        resume_data=structured_data
    )

    # create predefined coding sample (ID=1)
    create_sample_coding_set(user_id)

    return resume_id, file_url