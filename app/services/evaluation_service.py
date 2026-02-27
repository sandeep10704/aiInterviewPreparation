from datetime import datetime
from fastapi import HTTPException
from app.core.firebase import db
from app.services.llm_core import llm
from app.models.evaluation_schema import EvaluationSet


async def evaluate_technical_answers(user_id: str, technical_set_id: str):

    doc_ref = db.collection("users") \
        .document(user_id) \
        .collection("technical_questions") \
        .document(technical_set_id)

    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Technical set not found")

    data = doc.to_dict()

    questions = data.get("questions")
    user_answers = data.get("answers")

    if not user_answers:
        raise HTTPException(status_code=400, detail="Answers missing")

    evaluation_payload = []

    for q in questions:
        evaluation_payload.append({
            "question_no": q["question_no"],
            "question": q["question"],
            "correct_answer": q["answer"],
            "user_answer": user_answers.get(str(q["question_no"]), "")
        })

    structured_llm = llm.with_structured_output(EvaluationSet)

    prompt = f"""
    Evaluate each answer carefully.

    Scoring:
    0-3 = incorrect
    4-6 = partially correct
    7-8 = good
    9-10 = excellent

    Provide:
    - technical_feedback
    - motivation (encouraging, professional tone)
    - overall_score
    - overall_feedback

    Data:
    {evaluation_payload}
    """

    result = await structured_llm.ainvoke(prompt)

    evaluation_data = result.model_dump()

    # Store evaluation results
    doc_ref.update({
        "evaluations": evaluation_data["evaluations"],
        "overall_score": evaluation_data["overall_score"],
        "evaluated_at": datetime.utcnow(),
        "status": "evaluated"
    })

    return evaluation_data