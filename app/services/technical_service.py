import uuid
from datetime import datetime
from app.core.firebase import db
from app.services.technical_graph import technical_graph


async def generate_technical_set(user_id: str):

    # Get resume
    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()

    if not user_doc.exists:
        raise ValueError("User not found")

    resume_data = user_doc.to_dict().get("resume_data")

    if not resume_data:
        raise ValueError("Resume not parsed yet")

    # Run async graph
    result = await technical_graph.ainvoke({
        "resume_data": resume_data
    })

    technical_set_id = str(uuid.uuid4())
    questions = result["questions"]

    # Store at: technical_questions/{uid}/{technical_set_id}
    db.collection("technical_questions") \
      .document(user_id) \
      .collection("sets") \
      .document(technical_set_id) \
      .set({
          "technical_set_id": technical_set_id,
          "questions": questions,
          "answers": {},
          "status": "pending",
          "created_at": datetime.utcnow()
      })
    
    user_ref.collection("technical_questions") \
        .document(technical_set_id) \
        .set({
            "technical_set_id": technical_set_id,
            "questions": questions,
            "answers": {},
            "evaluations": [],
            "overall_score": None,
            "created_at": datetime.utcnow(),
            "submitted_at": None,
            "evaluated_at": None,
            "status": "pending"
        })

    return technical_set_id, questions

from app.services.evaluation_service import evaluate_technical_answers


async def submit_answers(user_id: str, technical_set_id: str, answers: dict):

    doc_ref = db.collection("users") \
        .document(user_id) \
        .collection("technical_questions") \
        .document(technical_set_id)

    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Technical set not found")

    # Store answers
    doc_ref.update({
        "answers": answers,
        "submitted_at": datetime.utcnow(),
        "status": "submitted"
    })

    # Evaluate immediately
    evaluation_data = await evaluate_technical_answers(user_id, technical_set_id)

    return evaluation_data