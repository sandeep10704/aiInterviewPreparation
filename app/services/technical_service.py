from http.client import HTTPException
import uuid
from datetime import datetime
from app.core.firebase import db
from app.services.technical_graph import technical_graph
from app.services.evaluation_service import evaluate_technical_answers

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




async def submit_answers(user_id: str, technical_set_id: str, answers: dict):

    user_doc_ref = db.collection("users") \
        .document(user_id) \
        .collection("technical_questions") \
        .document(technical_set_id)

    user_doc = user_doc_ref.get()

    
    if not user_doc.exists:

        master_ref = db.collection("technical_questions") \
            .document(user_id) \
            .collection("sets") \
            .document(technical_set_id)

        master_doc = master_ref.get()

        if not master_doc.exists:
            raise HTTPException(
                status_code=404,
                detail="Technical set not found anywhere"
            )

        master_data = master_doc.to_dict()

   
        user_doc_ref.set({
            "technical_set_id": technical_set_id,
            "questions": master_data.get("questions", []),
            "answers": {},
            "evaluations": [],
            "overall_score": None,
            "created_at": master_data.get("created_at"),
            "submitted_at": None,
            "evaluated_at": None,
            "status": "pending"
        })

    
    user_doc_ref.update({
        "answers": answers,
        "submitted_at": datetime.utcnow(),
        "status": "submitted"
    })

    evaluation_data = await evaluate_technical_answers(
        user_id,
        technical_set_id
    )

    return evaluation_data


async def get_master_technical_sets(user_id: str):

    sets_ref = db.collection("technical_questions") \
        .document(user_id) \
        .collection("sets")

    docs = sets_ref.stream()

    results = []

    for doc in docs:
        data = doc.to_dict()

        results.append({
            "technical_set_id": data.get("technical_set_id"),
            "status": data.get("status"),
            "created_at": data.get("created_at")
        })

    return results

async def get_or_create_user_technical_set(
    user_id: str,
    technical_set_id: str
):

    # ---------- USER DOC ----------
    user_doc_ref = db.collection("users") \
        .document(user_id) \
        .collection("technical_questions") \
        .document(technical_set_id)

    user_doc = user_doc_ref.get()

    # ✅ If already exists → return directly
    if user_doc.exists:
        data = user_doc.to_dict()

        return {
            "technical_set_id": technical_set_id,
            "questions": data.get("questions"),
            "status": data.get("status"),
            "answers": data.get("answers", {})
        }

    # ---------- MASTER DOC ----------
    master_ref = db.collection("technical_questions") \
        .document(user_id) \
        .collection("sets") \
        .document(technical_set_id)

    master_doc = master_ref.get()

    if not master_doc.exists:
        raise HTTPException(
            status_code=404,
            detail="Technical set not found"
        )

    master_data = master_doc.to_dict()

    # ---------- CREATE USER COPY ----------
    user_doc_ref.set({
        "technical_set_id": technical_set_id,
        "questions": master_data.get("questions", []),
        "answers": {},
        "evaluations": [],
        "overall_score": None,
        "created_at": master_data.get("created_at"),
        "submitted_at": None,
        "evaluated_at": None,
        "status": "pending",
        "started_at": datetime.utcnow()
    })

    return {
        "technical_set_id": technical_set_id,
        "questions": master_data.get("questions"),
        "status": "pending",
        "answers": {}
    }