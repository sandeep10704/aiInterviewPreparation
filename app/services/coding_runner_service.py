from fastapi import HTTPException
from app.core.firebase import db
from app.services.code_execution_service import run_code


async def run_user_code_preview(
    user_id: str,
    coding_set_id: str,
    question_no: int,
    code: str,
    language: str = "python"
):

    # ---------- GET USER CODING SET ----------
    doc_ref = db.collection("users") \
        .document(user_id) \
        .collection("coding_questions") \
        .document(coding_set_id)

    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(404, "Coding set not found")

    data = doc.to_dict()
    questions = data.get("questions", [])
    print("Questions:", questions)
    # ---------- FIND QUESTION ----------
    questions = data.get("questions", {})

    if isinstance(questions, dict):
        questions = list(questions.values())

    if question_no >= len(questions):
        raise HTTPException(404, "Question not found")

    question = questions[question_no]
    test_cases = question.get("test_cases", [])
    # ---------- RUN ONLY FIRST 3 TEST CASES ----------
    results = []
    passed = 0

    for test in test_cases[:3]:

        execution = await run_code(
            code,
            stdin_input=test["input"],
            language=language
        )

        output = execution["output"]

        success = output == test["output"]

        if success:
            passed += 1

        results.append({
            "input": test["input"],
            "expected": test["output"],
            "output": output,
            "passed": success
        })

    return {
        "question_no": question_no,
        "executed_cases": len(results),
        "passed": passed,
        "results": results
    }