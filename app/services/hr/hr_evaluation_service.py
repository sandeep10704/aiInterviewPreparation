from datetime import datetime
from fastapi import HTTPException
from app.core.firebase import db
from app.services.llm.llm_core import llm
from app.schemas.hr.hr_evaluation_schema import HREvaluationSet

async def evaluate_hr_answers(user_id, hr_set_id):

    doc_ref = db.collection("users") \
        .document(user_id) \
        .collection("hr_questions") \
        .document(hr_set_id)

    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(404, "HR set not found")

    data = doc.to_dict()

    payload = []

    for q in data["questions"]:
        payload.append({
            "question_no": q["question_no"],
            "question": q["question"],
            "ideal_answer": q["answer"],
            "user_answer": data["answers"].get(str(q["question_no"]), "")
        })

    structured_llm = llm.with_structured_output(HREvaluationSet)

    prompt = f"""
    Evaluate HR interview answers.

    Criteria:
    - communication clarity
    - confidence
    - professionalism
    - relevance

    Score each from 0–10.

    Data:
    {payload}
    """

    result = await structured_llm.ainvoke(prompt)

    evaluation = result.model_dump()

    doc_ref.update({
        "evaluations": evaluation["evaluations"],
        "overall_score": evaluation["overall_score"],
        "evaluated_at": datetime.utcnow(),
        "status": "evaluated"
    })

    return evaluation