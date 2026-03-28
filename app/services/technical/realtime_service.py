from datetime import datetime
from app.core.firebase import db
from app.services.llm.llm_core import llm
import asyncio
from pydantic import BaseModel
class SingleEvaluation(BaseModel):
    question_no: int
    score: int
    technical_feedback: str
    improvement_tip: str

async def update_answer_and_evaluate(
    user_id: str,
    technical_set_id: str,
    question_no: int,
    user_answer: str
):
    doc_ref = db.collection("users") \
        .document(user_id) \
        .collection("technical_questions") \
        .document(technical_set_id)

    doc = doc_ref.get()

    if not doc.exists:
        return {"error": "Technical set not found"}

    data = doc.to_dict()

    questions = data.get("questions", [])
    answers = data.get("answers", {})   # ✅ existing answers
    evaluations = data.get("evaluations", [])

    # ✅ UPDATE ONLY ONE ANSWER (important)
    answers[str(question_no)] = user_answer

    # 🔍 Find question
    target_q = next(
        (q for q in questions if q["question_no"] == question_no),
        None
    )

    if not target_q:
        return {"error": "Question not found"}

    # 🔥 Evaluate only this question
    prompt = f"""
    Evaluate this answer:

    Question: {target_q['question']}
    Correct Answer: {target_q['answer']}
    User Answer: {user_answer}

    Give:
    - score (0-10)
    - technical_feedback
    - improvement_tip
    """

    structured_llm = llm.with_structured_output(SingleEvaluation)

    print("Calling LLM...")

    result = await asyncio.to_thread(structured_llm.invoke, prompt)

    print("LLM response received")

    evaluation_data = result.model_dump()

    evaluation = {
        "question_no": question_no,
        "user_answer": user_answer,
        "feedback": str(result),
        "evaluated_at": datetime.utcnow().isoformat()
    }

    # ✅ Replace old evaluation if exists (important 🔥)
    evaluations = [
        e for e in evaluations if e["question_no"] != question_no
    ]
    evaluations.append(evaluation)

    # 💾 SAVE (same as submit_answers structure)
    doc_ref.update({
        "answers": answers,                  # ✅ SAME STRUCTURE
        "evaluations": evaluations,
        "submitted_at": datetime.utcnow(),   # behaves like submit
        "status": "in_progress"              # optional better than "submitted"
    })

    return evaluation