from datetime import datetime
from app.core.firebase import db
from app.services.llm.llm_core import llm
import asyncio
from pydantic import BaseModel


class HREvaluation(BaseModel):
    question_no: int
    communication_score: int
    confidence_score: int
    clarity_score: int
    feedback: str
    improvement_tip: str


async def update_hr_answer_and_evaluate(
    user_id: str,
    hr_set_id: str,
    question_no: int,
    user_answer: str
):
    doc_ref = db.collection("users") \
        .document(user_id) \
        .collection("hr_questions") \
        .document(hr_set_id)

    doc = doc_ref.get()

    if not doc.exists:
        return {"error": "HR set not found"}

    data = doc.to_dict()

    questions = data.get("questions", [])
    answers = data.get("answers", {})
    evaluations = data.get("evaluations", [])

    # ✅ Update single answer
    answers[str(question_no)] = user_answer

    # 🔍 Find question
    target_q = next(
        (q for q in questions if q["question_no"] == question_no),
        None
    )

    if not target_q:
        return {"error": "Question not found"}

    # 🧠 HR-focused prompt
    prompt = f"""
    Evaluate this HR interview answer:

    Question: {target_q['question']}
    User Answer: {user_answer}

    Evaluate based on:
    - communication (0-10)
    - confidence (0-10)
    - clarity (0-10)

    Give:
    - communication_score
    - confidence_score
    - clarity_score
    - feedback
    - improvement_tip
    """

    structured_llm = llm.with_structured_output(HREvaluation)

    result = await asyncio.to_thread(structured_llm.invoke, prompt)

    evaluation_data = result.model_dump()

    evaluation = {
        "question_no": question_no,
        "user_answer": user_answer,
        "evaluation": evaluation_data,
        "evaluated_at": datetime.utcnow().isoformat()
    }

    # ✅ Replace old evaluation
    evaluations = [
        e for e in evaluations if e["question_no"] != question_no
    ]
    evaluations.append(evaluation)

    # 💾 Save
    doc_ref.update({
        "answers": answers,
        "evaluations": evaluations,
        "status": "in_progress",
        "updated_at": datetime.utcnow()
    })

    return evaluation