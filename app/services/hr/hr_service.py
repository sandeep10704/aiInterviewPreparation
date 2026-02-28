import uuid
from datetime import datetime
from app.core.firebase import db
from app.services.hr.hr_graph import hr_graph


async def generate_hr_set(user_id: str, role: str, company: str):

    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()

    if not user_doc.exists:
        raise ValueError("User not found")

    resume_data = user_doc.to_dict().get("resume_data")

    if not resume_data:
        raise ValueError("Resume not parsed")

    result = await hr_graph.ainvoke({
        "role": role,
        "company": company,
        "resume_data": resume_data
    })

    hr_set_id = str(uuid.uuid4())
    questions = result["questions"]

    db.collection("users") \
        .document(user_id) \
        .collection("hr_questions") \
        .document(hr_set_id) \
        .set({
            "hr_set_id": hr_set_id,
            "role": role,
            "company": company,
            "questions": questions,
            "answers": {},
            "evaluations": [],
            "overall_score": None,
            "created_at": datetime.utcnow(),
            "status": "pending"
        })

    return hr_set_id, questions

from app.services.hr.hr_evaluation_service import evaluate_hr_answers

async def submit_hr_answers(user_id: str, hr_set_id: str, answers: dict):

    doc_ref = db.collection("users") \
        .document(user_id) \
        .collection("hr_questions") \
        .document(hr_set_id)

    doc_ref.update({
        "answers": answers,
        "submitted_at": datetime.utcnow(),
        "status": "submitted"
    })

    evaluation = await evaluate_hr_answers(user_id, hr_set_id)

    return evaluation