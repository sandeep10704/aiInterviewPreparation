import uuid
from datetime import datetime
from app.core.firebase import db
from app.services.coding.coding_graph import coding_graph
from app.services.coding.coding_evaluation_service import evaluate_code

async def generate_coding_set(user_id: str):

    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()

    if not user_doc.exists:
        raise ValueError("User not found")

    resume_data = user_doc.to_dict().get("resume_data")

    if not resume_data:
        raise ValueError("Resume missing")

    result = await coding_graph.ainvoke({
        "resume_data": resume_data
    })

    coding_set_id = str(uuid.uuid4())
    questions = result["questions"]

    user_ref.collection("coding_questions") \
        .document(coding_set_id) \
        .set({
            "coding_set_id": coding_set_id,
            "questions": questions,
            "answers": {},
            "status": "pending",
            "created_at": datetime.utcnow()
        })

    return coding_set_id, questions

async def submit_coding_solution(
    user_id: str,
    coding_set_id: str,
    question_index: int,
    code: str
):

    doc_ref = db.collection("users") \
        .document(user_id) \
        .collection("coding_questions") \
        .document(coding_set_id)

    doc = doc_ref.get()

    if not doc.exists:
        raise ValueError("Coding set not found")

    data = doc.to_dict()
    question = data["questions"][question_index]

    evaluation = await evaluate_code(
        code,
        question["test_cases"]
    )

    doc_ref.update({
        f"submissions.q{question_index}": {
            "code": code,
            "evaluation": evaluation,
            "submitted_at": datetime.utcnow()
        }
    })

    return evaluation